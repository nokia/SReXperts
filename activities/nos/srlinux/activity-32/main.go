// Copyright 2026 Nokia
// Licensed under the BSD 3-Clause License.
// SPDX-License-Identifier: BSD-3-Clause

package main

import (
	"context"
	"flag"
	"fmt"
	"io"
	"log/syslog"
	"os"
	"time"

	"github.com/openconfig/gnmic/pkg/api"
	"github.com/rs/zerolog"
	"github.com/srexperts/ndk-inventory/inventory"
	"github.com/srl-labs/bond"
	"gopkg.in/natefinch/lumberjack.v2"
)

const (
	grpcServerUnixSocketPrefix = "unix:///opt/srlinux/var/run/sr_grpc_server_"
	defaultGrpcServerName      = "insecure-mgmt"

	defaultUsername = "admin"
	defaultPassword = "NokiaSrl1!"
)

var version = "0.8.0"

func main() {
	versionFlag := flag.Bool("version", false, "print the version and exit")

	flag.Parse()

	if *versionFlag {
		fmt.Println(version)
		os.Exit(0)
	}

	logger := setupLogger()
	zerolog.SetGlobalLevel(zerolog.DebugLevel)

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	opts := []bond.Option{
		bond.WithLogger(&logger),
		bond.WithContext(ctx, cancel),
		bond.WithAppRootPath(inventory.AppRoot),
	}

	agent, errs := bond.NewAgent(inventory.AppName, opts...)
	for _, err := range errs {
		if err != nil {
			logger.Fatal().Err(err).Msg("Failed to create agent")
		}
	}

	target, err := api.NewTarget(
		api.Name("ndk"),
		api.Address(grpcServerUnixSocketPrefix+defaultGrpcServerName),
		api.Username(defaultUsername),
		api.Password(defaultPassword),
		api.Insecure(true),
		api.Timeout(10*time.Second),
	)
	if err != nil {
		logger.Fatal().Err(err).Msg("Failed to create gRPC target")
	}

	err = target.CreateGNMIClient(ctx)
	if err != nil {
		logger.Fatal().Err(err).Msg("Failed to create gRPC Client")
	}

	err = agent.Start()
	if err != nil {
		logger.Fatal().Err(err).Msg("Failed to start agent")
	}
	agent.GnmiTarget = target

	logger.Debug().Msg("Started agent")

	app := inventory.New(&logger, agent)
	app.Start(ctx)
}

func setupLogger() zerolog.Logger {
	var writers []io.Writer

	// the lab creates an empty file to indicate
	// that we run in dev mode. If file exists, we
	// log to console as well.
	_, err := os.Stat("/tmp/.ndk-dev-mode")
	if err == nil {
		const logTimeFormat = "2006-01-02 15:04:05 MST"

		consoleLogger := zerolog.ConsoleWriter{
			Out:        os.Stderr,
			TimeFormat: logTimeFormat,
			NoColor:    true,
		}

		writers = append(writers, consoleLogger)
	}

	const logFile = "/var/log/srlinux/debug/ndk_inventory.log"

	// A lumberjack logger with rotation settings.
	fileLogger := &lumberjack.Logger{
		Filename:   logFile,
		MaxSize:    2, // megabytes
		MaxBackups: 3,
		MaxAge:     28, // days
	}

	var zsyslog zerolog.SyslogWriter
	zsyslog, err = syslog.Dial("", "", syslog.LOG_DEBUG|syslog.LOG_LOCAL7, "ndk-inventory-go")
	if err != nil {
		panic(err)
	}

	writers = append(writers, fileLogger, zsyslog)

	mw := io.MultiWriter(writers...)

	return zerolog.New(mw).With().Caller().Timestamp().Logger()
}
