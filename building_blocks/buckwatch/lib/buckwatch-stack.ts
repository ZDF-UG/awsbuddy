import * as cdk from '@aws-cdk/core';
import * as iam from '@aws-cdk/aws-iam';
import * as sns from '@aws-cdk/aws-sns';
import * as subs from '@aws-cdk/aws-sns-subscriptions';

const productName = 'buckwatch'
export class BuckwatchStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);
    const NoteEmailSubscription = new cdk.CfnParameter(this, "NoteEmailSubscription", {
      type: "String",
      description: "EMail of the subscriber",
      default: "ayoub.umoru@zerodotfive.com"
    });

    const buckwatchRole = new iam.Role(this, 'buckwatch-role', {
      description: 'role responsible for the bucket watch.',
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
    })

    const notificationTopic = new sns.Topic(this, 'notification-topic',
      {
        displayName: `${productName}-topic`,
        topicName: `${productName}-topic`
      });
    notificationTopic.addSubscription(
      new subs.EmailSubscription(
        NoteEmailSubscription.valueAsString,
        {
          json: false
        }
      )
    )
  }

}
