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
      }
    ],
    test: async (z, bundle) => {
      let serverUrl = bundle.authData.serverAddress;
      
      // Ensure URL ends without trailing slash for consistency
      if (serverUrl.endsWith('/')) {
        serverUrl = serverUrl.slice(0, -1);
      }
      
      const response = await z.request(`${serverUrl}/`);
      
      // Check if response looks like our org-bridge server
      if (response.data && response.data.message === 'Org-Bridge API Server') {
        return response.data;
      } else {
        throw new Error('Server did not respond with expected org-bridge API format');
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
