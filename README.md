# 🐦🤖 Twimbot

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

