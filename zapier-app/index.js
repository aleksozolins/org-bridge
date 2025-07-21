module.exports = {
  // This is just shorthand to reference the installed dependencies you have.
  // Zapier will need to know these before we can upload.
  version: require('./package.json').version,
  platformVersion: require('zapier-platform-core').version,

  authentication: {
    type: 'custom',
    connectionLabel: '{{bundle.authData.serverAddress}}',
    fields: [
      {
        key: 'serverAddress',
        label: 'Server URL',
        type: 'string',
        required: true,
        helpText: 'The full URL of your org-bridge server including protocol and port (e.g., https://yourdomain.com:8247 or http://192.168.1.100:8247)',
        placeholder: 'https://yourdomain.com:8247'
      },
      {
        key: 'apiKey',
        label: 'API Key',
        type: 'string',
        required: true,
        helpText: 'Your org-bridge server API key (set via ORG_BRIDGE_API_KEY environment variable)',
        placeholder: 'your-api-key-here'
      }
    ],
    test: async (z, bundle) => {
      let serverUrl = bundle.authData.serverAddress;
      
      // Manual validation to ensure URL matches our expectations (addresses D026)
      if (!/^https?:\/\/[a-zA-Z0-9.-]+(:[0-9]+)?$/.test(serverUrl)) {
        throw new Error('Server URL must be a valid HTTP/HTTPS URL with hostname and optional port (e.g., https://yourdomain.com:8247)');
      }
      
      // Ensure URL ends without trailing slash for consistency
      if (serverUrl.endsWith('/')) {
        serverUrl = serverUrl.slice(0, -1);
      }
      
      // Test authentication by calling a protected endpoint
      const response = await z.request({
        url: `${serverUrl}/health`,
        headers: {
          'Authorization': `Bearer ${bundle.authData.apiKey}`
        }
      });
      
      if (response.data && response.data.status === 'healthy') {
        return response.data;
      } else {
        throw new Error('Server did not respond with expected health check format');
      }
    },
  },

  // If you want your trigger to show up, you better include it here!
  triggers: {},

  // If you want your searches to show up, you better include it here!
  searches: {},

  // If you want your creates to show up, you better include it here!
  creates: {
    create_todo: require('./creates/create_todo'),
  },

  resources: {},
};
