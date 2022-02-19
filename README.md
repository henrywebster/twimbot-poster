# 🐦🤖 Twimbot

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![codecov](https://codecov.io/gh/henrywebster/twimbot-poster/branch/main/graph/badge.svg?token=WU01UYGWPC)](https://codecov.io/gh/henrywebster/twimbot-poster)
![Build](https://github.com/henrywebster/twimbot-poster/actions/workflows/.github/workflows/deploy.yml/badge.svg)

`twimbot` (_twITTER imAGE bot_) is a [SAM](https://aws.amazon.com/serverless/sam/)-enabled tool for creating a [Twitter bot](https://blog.twitter.com/common-thread/en/topics/stories/2021/the-secret-world-of-good-bots) that periodically posts from a repository of images.

The project started as a way to learn Amazon Web Services and as a creative outlet for my own paintings, which can be found at [@2x2Bot](https://twitter.com/2x2Bot).

## Overview

`twimbot` uses the following AWS resources:
| Resource | Use |
| --- | ----------- |
| S3 | Image file storage |
| DynamoDB | Metadata |
| EventBridge | Scheduling |
| Lambda | Code execution |

### Diagram


![twimbot-v1](https://user-images.githubusercontent.com/14267649/154808683-3d744845-a2bc-4dd4-84e7-e2a86d059091.png)
