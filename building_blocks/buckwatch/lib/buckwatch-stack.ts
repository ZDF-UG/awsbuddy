import * as cdk from '@aws-cdk/core';
import * as iam from '@aws-cdk/aws-iam';

export class BuckwatchStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);
    const buckwatchRole = new iam.Role(this, 'buckwatch-role', {
      description: 'role responsible for the bucket watch.',
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
    })
  }
}
