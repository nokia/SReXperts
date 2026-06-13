// Copyright 2026 Nokia
// Licensed under the BSD 3-Clause License.
// SPDX-License-Identifier: BSD-3-Clause

package inventory

import (
	"encoding/json"
)

func (a *App) updateState() {
	jsData, err := json.Marshal(a.configState)
	if err != nil {
		a.logger.Info().Msgf("failed to marshal json data: %v", err)
		return
	}

	err = a.NDKAgent.UpdateState(AppRoot, string(jsData))
	if err != nil {
		a.logger.Error().Msgf("failed to update state: %v", err)
	}
}
