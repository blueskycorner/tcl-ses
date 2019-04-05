'use strict'
const merge = require('webpack-merge')
const prodEnv = require('./prod.env')

module.exports = merge(prodEnv, {
  NODE_ENV: '"production"',
  VUE_APP_BUILD_SIGNED_URL_ENDPOINT: '"https://c60esxid12.execute-api.us-east-1.amazonaws.com/dev/buildSignedUrlUpload"',
  AWS_AUTHORIZER: '"https://c60esxid12.execute-api.us-east-1.amazonaws.com/dev"',
  AWS_USER_POOL_ID: '"us-east-1_1yGbQLFkr"',
  AWS_USER_POOL_WEB_CLIENT_ID: '"bc543jaggp04qd2gg09jnr4il"'
})
