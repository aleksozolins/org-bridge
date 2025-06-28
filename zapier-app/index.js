module.exports = {
  // This is just shorthand to reference the installed dependencies you have.
  // Zapier will need to know these before we can upload.
  version: require('./package.json').version,
  platformVersion: require('zapier-platform-core').version,

  authentication: {
    type: 'custom',
    fields: [
      {
        key: 'serverAddress',
        label: 'Server Address',
        type: 'string',
        required: true,
        helpText: 'The domain or IP address of your org-bridge server (e.g., ozolins.xyz or 192.168.1.100)'
      },
      {
        key: 'serverPort',
        label: 'Server Port',
        type: 'string',
        required: true,
        default: '8247',
        helpText: 'The port your org-bridge server is running on'
      }
    ],
    test: async (z, bundle) => {
      const serverUrl = `http://${bundle.authData.serverAddress}:${bundle.authData.serverPort}`;
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
  creates: {},

  resources: {},
};
