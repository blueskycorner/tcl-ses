'use strict'
const merge = require('webpack-merge')
const prodEnv = require('./prod.env')

module.exports = merge(prodEnv, {
  NODE_ENV: '"development"',
  VUE_APP_BUILD_SIGNED_URL_ENDPOINT: '"https://c60esxid12.execute-api.us-east-1.amazonaws.com/dev/buildSignedUrlUpload"'
})
