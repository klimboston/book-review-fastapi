package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"

	amqp "github.com/rabbitmq/amqp091-go"
)

const reviewCreatedQueue = "review.created"

type ReviewCreatedEvent struct {
	Event    string `json:"event"`
	ReviewID int    `json:"review_id"`
	BookID   int    `json:"book_id"`
	Rating   int    `json:"rating"`
}

func consumeReviewCreated() error {
	rabbitURL := fmt.Sprintf(
		"amqp://%s:%s@%s:%s/",
		os.Getenv("RABBITMQ_USER"),
		os.Getenv("RABBITMQ_PASSWORD"),
		os.Getenv("RABBITMQ_HOST"),
		os.Getenv("RABBITMQ_PORT"),
	)

	conn, err := amqp.Dial(rabbitURL)
	if err != nil {
		return fmt.Errorf("connect to RabbitMQ: %w", err)
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		return fmt.Errorf("create RabbitMQ channel: %w", err)
	}
	defer ch.Close()

	queue, err := ch.QueueDeclare(
		reviewCreatedQueue,
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		return fmt.Errorf("declare queue: %w", err)
	}

	messages, err := ch.Consume(
		queue.Name,
		"",
		false,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		return fmt.Errorf("start consuming messages: %w", err)
	}

	log.Printf("Listening on queue %q", queue.Name)

	for message := range messages {
		var event ReviewCreatedEvent

		if err := json.Unmarshal(message.Body, &event); err != nil {
			log.Printf("Invalid event JSON: %v", err)
			if nackErr := message.Nack(false, false); nackErr != nil {
				log.Printf("Nack failed: %v", nackErr)
			}
			continue
		}

		log.Printf(
			"Received event=%s review_id=%d book_id=%d rating=%d",
			event.Event,
			event.ReviewID,
			event.BookID,
			event.Rating,
		)

		if err := message.Ack(false); err != nil {
			log.Printf("Ack failed: %v", err)
		}
	}

	return nil
}
