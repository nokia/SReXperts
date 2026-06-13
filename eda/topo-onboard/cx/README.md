# Deploying in CX

## Deploy the fabric and services

```bash
ls -1 eda/fabric | grep -v 20 | \
xargs -I {} kubectl apply -f eda/fabric/{}
```
