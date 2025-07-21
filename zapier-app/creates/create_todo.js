const perform = async (z, bundle) => {
  // Get the full server URL (now includes protocol and port)
  let serverUrl = bundle.authData.serverAddress;
  
  // Manual validation to ensure URL matches our expectations (addresses D026)
  if (!/^https?:\/\/[a-zA-Z0-9.-]+(:[0-9]+)?$/.test(serverUrl)) {
    throw new Error('Server URL must be a valid HTTP/HTTPS URL with hostname and optional port');
  }
  
  // Ensure URL ends without trailing slash for consistency
  if (serverUrl.endsWith('/')) {
    serverUrl = serverUrl.slice(0, -1);
  }
  
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
    file_name: bundle.inputData.file_name,
    heading: bundle.inputData.heading
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
}

module.exports = {
  key: 'create_todo',
  noun: 'TODO',
  display: {
    label: 'Create TODO',
    description: 'Creates a new TODO item in your org-mode files',
  },
  operation: {
    sample: {
      id: 'FCD64514-6072-4C90-81A7-F726C299843D',
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
      file_path: '/path/to/inbox.org',
      heading: 'Work Projects'
    },
    inputFields: [
      {
        key: 'file_name',
        label: 'Org File',
        type: 'string',
        placeholder: 'inbox.org',
        helpText: 'Which org file to add this TODO to. Leave blank to use your default inbox file. Include the `.org` extension.'
      },
      {
        key: 'heading',
        label: 'Heading',
        type: 'string',
        placeholder: 'Zapier',
        helpText: 'Which heading to file this TODO under. Must match exactly (case-sensitive, ignoring tags). If heading doesn\'t exist, it will be created as a top-level heading.'
      },
      {
        key: 'title',
        label: 'TODO Title',
        type: 'string',
        required: true,
        placeholder: 'Call client about project update',
        helpText: 'The main description of what needs to be done. This will be the heading text in your org file.'
      },
      {
        key: 'state',
        label: 'TODO State',
        type: 'string',
        default: 'TODO',
        choices: ['TODO', 'NEXT', 'WAITING', 'DONE'],
        helpText: 'The current state of this task. **TODO** = not started, **NEXT** = ready to work on, **WAITING** = blocked, **DONE** = completed.'
      },
      {
        key: 'priority',
        label: 'Priority',
        type: 'string',
        choices: ['A', 'B', 'C'],
        helpText: 'Task priority level. **A** = highest/urgent, **B** = medium/important, **C** = low/someday. Leave blank for no priority.'
      },
      {
        key: 'tags',
        label: 'Tags',
        type: 'string',
        placeholder: '@work, urgent, meeting',
        helpText: 'Comma-separated tags to categorize this TODO. These help with filtering and organization in org-mode.'
      },
      {
        key: 'scheduled',
        label: 'Scheduled Date & Time',
        type: 'datetime',
        placeholder: 'today 2pm',
        altersDynamicFields: true,
        helpText: 'When you plan to work on this task. In org-mode, this appears in your agenda on the scheduled date.'
      },
      function (z, bundle) {
        if (bundle.inputData.scheduled) {
          return {
            key: 'include_scheduled_time',
            label: 'Include Scheduled Time',
            type: 'boolean',
            default: 'false',
            helpText: 'Include the specific time in the scheduled timestamp. **True** = `<2025-01-20 14:30>`, **False** = `<2025-01-20>`'
          };
        }
        return [];
      },
      {
        key: 'deadline',
        label: 'Deadline Date & Time',
        type: 'datetime',
        placeholder: 'tomorrow 8am',
        altersDynamicFields: true,
        helpText: 'Hard deadline for this task. Org-mode will show warnings as the deadline approaches in your agenda.'
      },
      function (z, bundle) {
        if (bundle.inputData.deadline) {
          return {
            key: 'include_deadline_time',
            label: 'Include Deadline Time',
            type: 'boolean',
            default: 'false',
            helpText: 'Include the specific time in the deadline timestamp. **True** = `<2025-01-22 16:45>`, **False** = `<2025-01-22>`'
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
            helpText: 'Enable recurring pattern for this task. Perfect for habits, regular meetings, or recurring deadlines.'
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
              helpText: 'Which date should repeat? **Scheduled** = when to work on it, **Deadline** = when it\'s due.'
            });
          }
          
          fields.push(
            {
              key: 'repeat_every',
              label: 'Repeat Every',
              type: 'integer',
              required: true,
              placeholder: '1',
              helpText: 'How many intervals between repeats? **1** = every week, **2** = every 2 weeks, **6** = every 6 hours.'
            },
            {
              key: 'repeat_unit',
              label: 'Repeat Unit',
              type: 'string',
              choices: ['hours', 'days', 'weeks', 'months', 'years'],
              required: true,
              helpText: 'Time unit for recurring pattern. Creates org-mode syntax: **hours** → `h`, **days** → `d`, **weeks** → `w`, **months** → `m`, **years** → `y`'
            },
            {
              key: 'repeat_type',
              label: 'Repeat Type',
              type: 'string',
              choices: ['standard', 'from_completion', 'catch_up'],
              required: true,
              helpText: 'How repeating works: **standard** = `+1w` (fixed schedule), **from_completion** = `.+1w` (from when you finish), **catch_up** = `++1w` (shows all missed occurrences)'
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
        helpText: '**Key-value pairs** for org-mode properties drawer (e.g., `CATEGORY: work`, `PROJECT: website`). **Note:** A unique `ID` property will be automatically generated for every TODO.'
      },
      {
        key: 'body',
        label: 'Body/Notes',
        type: 'text',
        placeholder: 'Additional details, meeting agenda, project requirements...',
        helpText: 'Additional content, notes, or details for this TODO. This text will appear below the heading in your org file.'
      }
    ],
    perform,
  },
}; 