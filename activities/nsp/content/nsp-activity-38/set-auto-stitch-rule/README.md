# Get & Set Auto Stitch Setting

Note: Prepopulate leafref action won't work from IBSF UI.

| File Name                    | Purpose / Description                                                                 |
|------------------------------|----------------------------------------------------------------------------------------|
| `get-auto-stitch-setting.yaml` | Used for viewing the current state of auto-stitch rules                              |
| `auto-stitch-setting.jinja`   | Template used by `get-auto-stitch-setting` to pretty print the result                 |
| `set-auto-stitch-rule.yaml`   | Defines and sets the auto-stitch rules based on user selection                        |
| `set-auto-stitch-rule.json`   | Input form used by `set-auto-stitch-rule`                                             |
| `get-auto-stitch-algo.action` | Action used for prepopulating inputs in `set-auto-stitch-rule`                        |


## Screenshot

![Execution](./images/execution.png)

## Author

<siva.sivakumar@nokia.com>
