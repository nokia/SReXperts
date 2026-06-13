// Copyright 2026 Nokia
// Licensed under the BSD 3-Clause License.
// SPDX-License-Identifier: BSD-3-Clause

package inventory

import (
	"encoding/json"
)

type ConfigState struct {
	// Location is the non-granular location string
	Location string `json:"location,omitempty"`
}

func (a *App) loadConfig() {
	a.configState = &ConfigState{} // clear the configState
	if a.NDKAgent.Notifications.FullConfig != nil {
		a.logger.Info().Msgf("configuration JSON: %s", a.NDKAgent.Notifications.FullConfig)
		err := json.Unmarshal(a.NDKAgent.Notifications.FullConfig, a.configState)
		if err != nil {
			a.logger.Error().Err(err).Msg("Failed to unmarshal config")
		}
	}
}

func (a *App) processConfig() {
	// This is where the code processing every single configuration update goes
}
