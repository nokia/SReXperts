// Copyright 2026 Nokia
// Licensed under the BSD 3-Clause License.
// SPDX-License-Identifier: BSD-3-Clause

package inventory

import (
	"context"

	"github.com/rs/zerolog"
	"github.com/srl-labs/bond"
)

const (
	AppName = "inventory"
	AppRoot = "/" + AppName
)

type App struct {
	Name string
	// configState holds the application configuration and state.
	configState *ConfigState
	logger      *zerolog.Logger
	NDKAgent    *bond.Agent
}

func New(logger *zerolog.Logger, agent *bond.Agent) *App {
	return &App{
		Name:     AppName,
		NDKAgent: agent,
		logger:   logger,
	}
}

func (a *App) Start(ctx context.Context) {
	for {
		select {
		case <-a.NDKAgent.Notifications.FullConfigReceived:
			a.logger.Debug().Msg("Received full config")

			a.loadConfig()

			a.processConfig()

			a.updateState()

		case <-ctx.Done():
			return
		}
	}
}
