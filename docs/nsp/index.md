---
tags:
  - NSP
  - Artifact Manager
  - Intent Manager
  - Workflow Manager
  - Device Operations
  - Visual Studio Code
---

# Network Services Platform (NSP)

This section contains the activities for the NSP stream of the 2025 SReXperts hackathon.

At Nokia, we’re committed to deliver the best experience — whether you're working with our industry-leading routing hardware, our model-driven
network operating systems (SR OS and SR Linux), or our advanced network management solutions, NSP (Network Services Platform) and EDA.

During the 2025 Hackathon, you’ll get the chance to explore and experiment with our network technologies - whether it’s through on-box automation
or integrating open-source tools. But we take it one step further. With Nokia’s Network Services Platform (NSP), you gain a powerful automation
framework that provides end-to-end network visibility and enables you to provision, monitor, and assure your services and infrastructure with confidence.

NSP is built for developers, network engineers, and operations teams who want to move beyond manual tasks and into a programmable, intent-driven world.
NSP abstracts network complexity by letting you define what you want, not how to do it. Intent models are mapped to device-specific configurations,
enabling consistent service and policy enforcement. You can create reusable imperative automation workflows while triggering them via API, GUI,
schedules, or events (internal and external). You can run those workflows at scale using Device Operations while NSP provides you with advanced
monitoring and execution control, giving control to the operator as needed.

All of NSP is enabled by rich OpenAPIs, but not limited to automation build within NSP.
It allows seamless integration with your CI/CD pipelines, north-bound 3rd-party systems, and open-source toolchains.

# Visual Studio Code - Your NSP IDE

While NSP WebUI is the quick choice for developing automation use-cases, we are promoting the use of Visual Studio Code as Integrated
Development Environment by choice. If you have the ability to install VS Code on your computer, just do it. It's powerful! It's free!
And it's fun! If you are into programming, you may already have it... If you cannot install it for administrative reasons: Don't Worry!
There is `code-server` which is basically a server-hosted version of VS Code that can be accessed using your web-browser, coming with
the same great experience. The good news: We've got code-server deployed in the hackathon labs, so it is just waiting for
you to connect.

NOKIA is actively contributing VS Code extensions to improve Developer eXperience around our networking products and technologies being used.
In this hackathon, you have the opportunity to use the following extensions contributed by Nokia in action:

* [NSP Intent Manager extension](https://github.com/nokia/vscode-intent-manager)
* [NSP Workflow Manager extension](https://github.com/nokia/vscode-workflow-manager)
* [NSP Artifact Manager extension](https://marketplace.visualstudio.com/items?itemName=Nokia.artifactadminstrator)
* [NSP connect extension](https://marketplace.visualstudio.com/items?itemName=Nokia.nsp-connect)
* [EDA extension](https://marketplace.visualstudio.com/items?itemName=eda-labs.vscode-eda)
* [Containerlab extension](https://github.com/srl-labs/vscode-containerlab)
* [NETCONF extension](https://github.com/nokia/vscode-netconf)

/// warning | Disclaimer
The VS Code Extensions contributed by Nokia are community-driven open-source initiatives.

If you run into problems, please issue your support requests and provide feedback to the community directly,
by raising issues on GitHub! If you've found a solution that works for you, we are happy for everybody contributing
code changes back to the project. By this you become part of our community helping it to grow.
///

## Tackling the activities

A number of activities have been created for you to follow, separated by our rough estimation of difficulty level (opinions may vary :smile:).
Feel free to attempt any of them.

Remind, activities are to provide you with ideas and guidance. If you want to go freestyle, just do it! We will help you at our best ability.
However, it's your opportunity to practice and learn! Don't just come with a crazy idea and expect the hackathon support to solve it for you.

### Standalone activities and not in order

Each activity is a stand alone use-case.  Each has a scenario, a set of objectives and lots of information for you to learn and practice.

**The activities are not in order**. You do not need to start at the top and work your way down.
We recommend instead that you take a look through activities that sound interesting and tackle the ones that you feel would give you the most benefit, whether that's solidifying knoweldge you already have or learning a totally new technology.

### Isolated networks, Shared NSP

Each group's network is self-contained. Network changes you make will not effect other group's activities and no-one will get upset if you break everything, so dive right in and don't be afraid to try it and see.

However, we are using a single, shared NSP instance.
Access control is widely in place to avoid people step on each others toes.
Make sure to name your automation artifacts uniquely adding your group-id to avoid surprises.

### Help us make the hackathon the best it can be

Each year we review the feedback and lessons learned from the previous years hackathon as we want to continually deliver the best, and most useful, experience we can.  To help us do this we have two asks:

- You will notice, next to each task there is a blue `Start` button.  When you start to attempt each task, would you please click the button.
- When you complete an activity (or even if you don't manage to complete it), you will find a very short questionairre at the end.  Would you please fill it out as honestly as you feel able to, we won't be offended if you think something was awful, and equally we like praise as much as the next person!

These two small asks will help us continue to improve your experience for when you return next year!

## Help!

If you need help at anytime you have a few options:

- Take a look at the reference material and hints provided in the activities.
- Ask other members of your group, or other groups for help.  Collaboration is one of the best elements of the hackathon.
- Put your hand up or otherwise grab the attention of one of the team to assist you (that is what they are there for so please use them!)

## Ask us (almost) anything

Not only are the team here to help you with anything in the hackathon, but they also have a wide range of knowledge about Nokia, our products, our services and our technologies.  Please ask anything that's on your mind.

We'd also love to hear from you about what you're doing with automation and programmability in your network and any of the amazing or more challenging things you are working on.
