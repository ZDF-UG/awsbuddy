#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from '@aws-cdk/core';
import { BuckwatchStack } from '../lib/buckwatch-stack';

const product = "buckwatch"
const app = new cdk.App();
const stack = new BuckwatchStack(app, `${product}-stack`);

[stack].forEach(stack => {
    cdk.Tag.add(stack, 'ProductName', product);
});

