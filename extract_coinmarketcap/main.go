package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"
	"github.com/nikoksr/notify"
	"github.com/nikoksr/notify/service/discord"
)

type Coinmarketcap struct {
	Data []struct {
		Id     int    `json:"id"`
		Name   string `json:"name"`
		Symbol string `json:"symbol"`
		Slug   string `json:"slug"`
		Quote  struct {
			USD struct {
				Price float64 `json:"price"`
			} `json:"USD"`
		} `json:"quote"`
	} `json:"data"`
}

var Db sqlx.DB

func main() {
	Db = *initDb()
	defer Db.Close()
	for _, i := range [2]string{"1", "5001"} {
		body := extractFromCmc(i)
		cmc := processBodyIntoStruct(body)
		pushCoinsIntoDb(cmc)
		pushPricesIntoDb(cmc)
	}
}

func initDb() (db *sqlx.DB) {
	DbUrl := fmt.Sprintf(
		"postgres://%s:%s@%s:%s/%s",
		os.Getenv("TL_DB_USER"),
		os.Getenv("TL_DB_PASS"),
		os.Getenv("TL_DB_HOST"),
		os.Getenv("TL_DB_PORT"),
		os.Getenv("TL_DB_NAME"),
	)
	db, err := sqlx.Connect("postgres", DbUrl)
	if err != nil {
		sendNotification("error", err.Error())
		panic(err.Error())
	}
	return db
}

func extractFromCmc(starting string) (body []byte) {
	req, err := http.NewRequest(
		"GET",
		os.Getenv("CMC_API_URL"),
		nil,
	)
	if err != nil {
		sendNotification("error", err.Error())
		panic(err.Error())
	}
	q := req.URL.Query()
	q.Add("start", starting)
	q.Add("limit", "5000")
	q.Add("convert", "usd")
	req.URL.RawQuery = q.Encode()
	req.Header.Add(
		"Accepts",
		"application/json",
	)
	req.Header.Add(
		"X-CMC_PRO_API_KEY",
		os.Getenv("CMC_API_KEY"),
	)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		sendNotification("error", err.Error())
		panic(err.Error())
	}
	defer resp.Body.Close()
	body, err = ioutil.ReadAll(resp.Body)
	if err != nil {
		sendNotification("error", err.Error())
		panic(err.Error())
	}
	return body
}

func processBodyIntoStruct(body []byte) (cmc Coinmarketcap) {
	err := json.Unmarshal(body, &cmc)
	if err != nil {
		sendNotification("error", err.Error())
		panic(err.Error())
	}
	return
}

func pushCoinsIntoDb(cmc Coinmarketcap) {
	valueStrings := []string{}
	valueArgs := []interface{}{}
	for i, elem := range cmc.Data {
		str1 := "$" + strconv.Itoa(1+i*4) + ","
		str2 := "$" + strconv.Itoa(2+i*4) + ","
		str3 := "$" + strconv.Itoa(3+i*4) + ","
		str4 := "$" + strconv.Itoa(4+i*4)
		str_n := "(" + str1 + str2 + str3 + str4 + ")"
		valueStrings = append(valueStrings, str_n)
		valueArgs = append(valueArgs, elem.Id)
		valueArgs = append(valueArgs, elem.Name)
		valueArgs = append(valueArgs, elem.Symbol)
		valueArgs = append(valueArgs, elem.Slug)
	}
	smt := `
		INSERT INTO coins (coinid, name, symbol, slug)
		VALUES %s
		ON CONFLICT DO NOTHING;`
	smt = fmt.Sprintf(smt, strings.Join(valueStrings, ","))

	_, err := Db.Exec(smt, valueArgs...)
	if err != nil {
		sendNotification("error", err.Error())
		panic(err.Error())
	}
}

func pushPricesIntoDb(cmc Coinmarketcap) {
	valueStrings := []string{}
	valueArgs := []interface{}{}
	timeNow := time.Now()
	for i, elem := range cmc.Data {
		str1 := "$" + strconv.Itoa(1+i*3) + ","
		str2 := "$" + strconv.Itoa(2+i*3) + ","
		str3 := "$" + strconv.Itoa(3+i*3)
		str_n := "(" + str1 + str2 + str3 + ")"
		valueStrings = append(valueStrings, str_n)
		valueArgs = append(valueArgs, timeNow)
		valueArgs = append(valueArgs, elem.Id)
		valueArgs = append(valueArgs, elem.Quote.USD.Price)
	}
	prices_smt := `
		INSERT INTO prices (createdat, coinid, price)
		VALUES %s;`
	prices_smt = fmt.Sprintf(
		prices_smt,
		strings.Join(valueStrings, ","),
	)
	_, err := Db.Exec(prices_smt, valueArgs...)
	if err != nil {
		sendNotification("error", err.Error())
		panic(err.Error())
	}
	last_prices_smt := `
		INSERT INTO lastprices (updatedat, coinid, price)
		VALUES %s
		ON CONFLICT(coinid)
		DO UPDATE SET
			updatedat = EXCLUDED.updatedat,
			price = EXCLUDED.price;`
	last_prices_smt = fmt.Sprintf(
		last_prices_smt,
		strings.Join(valueStrings, ","),
	)
	_, err = Db.Exec(last_prices_smt, valueArgs...)
	if err != nil {
		sendNotification("error", err.Error())
		panic(err.Error())
	}
}

func sendNotification(title string, msg string) {
	discordService := discord.New()
	_ = discordService.AuthenticateWithBotToken(os.Getenv("DISCORD_BOT_ID"))
	discordService.AddReceivers(os.Getenv("DISCORD_CHANNEL_CMC"))
	notifier := notify.New()
	notifier.UseServices(discordService)
	_ = notifier.Send(
		context.Background(),
		title,
		msg,
	)
}
