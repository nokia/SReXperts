MKDOCS_INS_VER = 9.6.9-insiders-4.53.16-hellt

.PHONY: docs
docs:
	docker run --rm -v $$(pwd):/docs --entrypoint mkdocs registry.srlinux.dev/pub/mkdocs-material-insiders:$(MKDOCS_INS_VER) build --clean --strict

# serve the site locally using mkdocs-material insiders container
.PHONY: serve-insiders
serve-insiders:
	docker run -it --rm -p 8001:8000 -v $$(pwd):/docs registry.srlinux.dev/pub/mkdocs-material-insiders:$(MKDOCS_INS_VER)

# serve the site locally using mkdocs-material insiders container using dirty-reloader
.PHONY: serve-insiders-dirty
serve-insiders-dirty:
	docker run -it --rm -p 8001:8000 -v $$(pwd):/docs registry.srlinux.dev/pub/mkdocs-material-insiders:$(MKDOCS_INS_VER) serve --dirtyreload -a 0.0.0.0:8000

.PHONY: serve-docs
serve-docs: serve-insiders

.PHONY: htmltest
htmltest:
	docker run --rm -v $$(pwd):/docs --entrypoint mkdocs registry.srlinux.dev/pub/mkdocs-material-insiders:$(MKDOCS_INS_VER) build --clean --strict
	docker run --rm -v $$(pwd):/test wjdp/htmltest --conf ./site/htmltest.yml
	rm -rf ./site

build-insiders:
	docker run -v $$(pwd):/docs --entrypoint mkdocs registry.srlinux.dev/pub/mkdocs-material-insiders:$(MKDOCS_INS_VER) build --clean --strict

push-docs: # push docs to gh-pages branch manually. Use when pipeline misbehaves
	docker run -v ${SSH_AUTH_SOCK}:/ssh-agent --env SSH_AUTH_SOCK=/ssh-agent --env GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" -v $$(pwd):/docs --entrypoint mkdocs ghcr.io/srl-labs/mkdocs-material-insiders:$(MKDOCS_INS_VER) gh-deploy --force --strict

add-no-index: # replace noindex commen in main template to include robots noindex instruction. This is needed prior pushing to staging, so that staging is not indexed by robots
	sed -i 's/<!-- NOINDEX -->/<meta name="robots" content="noindex">/g' docs/overrides/main.html

