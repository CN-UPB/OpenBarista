#!/usr/bin/env bash

ps aux | grep deploymentd | awk '{print $2}' | xargs kill -9


