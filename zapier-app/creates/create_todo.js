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
    include_scheduled_time: bundle.inputData.include_scheduled_time || false,
    include_deadline_time: bundle.inputData.include_deadline_time || false,
    is_recurring: bundle.inputData.is_recurring || false,
    recurring_field: bundle.inputData.recurring_field,
    repeat_every: bundle.inputData.repeat_every ? parseInt(bundle.inputData.repeat_every) : null,
    repeat_unit: bundle.inputData.repeat_unit,
    repeat_type: bundle.inputData.repeat_type,
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
    sample: {
      id: 'todo_1642712345',
      title: 'Weekly team meeting',
      state: 'TODO',
      priority: 'B',
      tags: ['work', 'meeting'],
      scheduled: '2025-01-20T14:00:00',
      deadline: null,
      include_scheduled_time: true,
      include_deadline_time: false,
      is_recurring: true,
      recurring_field: 'scheduled',
      repeat_every: 1,
      repeat_unit: 'weeks',
      repeat_type: 'standard',
      properties: {
        'CATEGORY': 'work',
        'EFFORT': '1:00'
      },
      body: 'Discuss weekly goals and blockers',
      file_path: '/path/to/inbox.txt'
    },
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
        label: 'Scheduled Date & Time',
        type: 'datetime',
        altersDynamicFields: true,
        helpText: 'When to schedule this TODO (date and optional time)'
      },
      function (z, bundle) {
        if (bundle.inputData.scheduled) {
          return {
            key: 'include_scheduled_time',
            label: 'Include Scheduled Time',
            type: 'boolean',
            default: 'false',
            helpText: 'Include the time component in the scheduled timestamp'
          };
        }
        return [];
      },
      {
        key: 'deadline',
        label: 'Deadline Date & Time',
        type: 'datetime',
        altersDynamicFields: true,
        helpText: 'Deadline for this TODO (date and optional time)'
      },
      function (z, bundle) {
        if (bundle.inputData.deadline) {
          return {
            key: 'include_deadline_time',
            label: 'Include Deadline Time',
            type: 'boolean',
            default: 'false',
            helpText: 'Include the time component in the deadline timestamp'
          };
        }
        return [];
      },
      function (z, bundle) {
        if (bundle.inputData.scheduled || bundle.inputData.deadline) {
          return {
            key: 'is_recurring',
            label: 'Make Recurring',
            type: 'boolean',
            default: 'false',
            altersDynamicFields: true,
            helpText: 'Enable recurring pattern for this TODO'
          };
        }
        return [];
      },
      function (z, bundle) {
        if (bundle.inputData.is_recurring === 'true' || bundle.inputData.is_recurring === true) {
          const fields = [];
          
          // Build choices dynamically based on which date fields are set
          const recurringChoices = [];
          if (bundle.inputData.scheduled) recurringChoices.push('scheduled');
          if (bundle.inputData.deadline) recurringChoices.push('deadline');
          
          if (recurringChoices.length > 0) {
            fields.push({
              key: 'recurring_field',
              label: 'Recurring Field',
              type: 'string',
              choices: recurringChoices,
              required: true,
              helpText: 'Which date field should have the recurring pattern applied'
            });
          }
          
          fields.push(
            {
              key: 'repeat_every',
              label: 'Repeat Every',
              type: 'integer',
              required: true,
              helpText: 'Number of intervals (e.g., 1 for every week, 2 for every 2 weeks)'
            },
            {
              key: 'repeat_unit',
              label: 'Repeat Unit',
              type: 'string',
              choices: ['hours', 'days', 'weeks', 'months', 'years'],
              required: true,
              helpText: 'Time unit for recurring pattern. Examples: hours→h, days→d, weeks→w, months→m, years→y'
            },
            {
              key: 'repeat_type',
              label: 'Repeat Type',
              type: 'string',
              choices: ['standard', 'from_completion', 'catch_up'],
              required: true,
              helpText: 'standard: +1w (fixed schedule), from_completion: .+1w (from when done), catch_up: ++1w (shows missed occurrences)'
            }
          );
          
          return fields;
        }
        return [];
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