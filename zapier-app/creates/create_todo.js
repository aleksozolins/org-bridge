const perform = async (z, bundle) => {
  const serverUrl = `http://${bundle.authData.serverAddress}:${bundle.authData.serverPort}`;
  
  // Build the request body from input fields
  const requestBody = {
    title: bundle.inputData.title,
    state: bundle.inputData.state || 'TODO',
    priority: bundle.inputData.priority,
    tags: bundle.inputData.tags ? bundle.inputData.tags.split(',').map(tag => tag.trim()) : [],
    scheduled: bundle.inputData.scheduled,
    deadline: bundle.inputData.deadline,
    properties: bundle.inputData.properties,
    body: bundle.inputData.body,
    file_name: bundle.inputData.file_name
  };

  const response = await z.request({
    url: `${serverUrl}/todos`,
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: requestBody,
  });

  return response.data;
};

module.exports = {
  key: 'create_todo',
  noun: 'TODO',
  display: {
    label: 'Create TODO',
    description: 'Creates a new TODO item in your org-mode files',
  },
  operation: {
    inputFields: [
      {
        key: 'title',
        label: 'TODO Title',
        type: 'string',
        required: true,
        helpText: 'The title/description of the TODO item'
      },
      {
        key: 'state',
        label: 'TODO State',
        type: 'string',
        default: 'TODO',
        choices: ['TODO', 'NEXT', 'WAITING', 'DONE'],
        helpText: 'The state of the TODO item'
      },
      {
        key: 'priority',
        label: 'Priority',
        type: 'string',
        choices: ['A', 'B', 'C'],
        helpText: 'Priority level (A=highest, C=lowest)'
      },
      {
        key: 'tags',
        label: 'Tags',
        type: 'string',
        helpText: 'Comma-separated tags (e.g., work, urgent, meeting)'
      },
      {
        key: 'scheduled',
        label: 'Scheduled Date',
        type: 'string',
        helpText: 'When to schedule this TODO (YYYY-MM-DD format)'
      },
      {
        key: 'deadline',
        label: 'Deadline',
        type: 'string',
        helpText: 'Deadline for this TODO (YYYY-MM-DD format)'
      },
      {
        key: 'properties',
        label: 'Properties',
        type: 'string',
        dict: true,
        helpText: 'Key-value pairs for org-mode properties drawer (e.g., FROM: email, PROJECT: work)'
      },
      {
        key: 'body',
        label: 'Body/Notes',
        type: 'text',
        helpText: 'Additional content, notes, or details for this TODO'
      },
      {
        key: 'file_name',
        label: 'File Name',
        type: 'string',
        helpText: 'Which org file to add to (leave blank for inbox.txt)'
      }
    ],
    perform,
  },
}; 