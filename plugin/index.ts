import '@logseq/libs'
import { SettingSchemaDesc } from '@logseq/libs/dist/LSPlugin';
import * as io from 'socket.io-client'

const delay = ms => new Promise(res => setTimeout(res, ms));

const settingsSchema: SettingSchemaDesc[] = [
  {
    key: "socketioServerURL",
    type: "string",
    default: "http://localhost:3000",
    title: "SocketIO Server URL",
    description: "The URL of the SocketIO server to connect to.",
  },
]

async function settings_are_valid() {
  const server_url = logseq.settings!["socketioServerURL"]
  if (!server_url) {
    console.error("Server URL not configured for SocketIO.")
    logseq.App.showMsg(
      "Please configure server URL for SocketIO.",
      "error"
    )
    return false
  }
  return true
}

async function main() {
  // Use initial settings schema
  console.log("Using initial settings schema.")
  logseq.useSettingsSchema(settingsSchema)

  if (!await settings_are_valid()) {
    // Settings are invalid, exit
    console.error("SocketIO settings are invalid, exiting.")
    return
  }

  const socket = io.connect(logseq.settings!["socketioServerURL"], {
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    reconnectionAttempts: Infinity,
    transports: ['websocket'],
  })

  socket.on('connect', async () => {
    console.log("Connected to plugin server.")
    socket.emit('ready')
    socket.emit('graph', await logseq.App.getCurrentGraph())
  })

  socket.on('disconnect', async () => {
    console.log("Disconnected from plugin server.")
    // Revert settings schema to initial schema
    logseq.useSettingsSchema(settingsSchema)
  })

  socket.on("useSettingsSchema", async (settings) => {
    const settings_schema = <SettingSchemaDesc[]>settings
    logseq.useSettingsSchema(settings_schema);
    console.log("SettingsSchema applied:", settings_schema)
  })

  socket.on("Editor.registerSlashCommand", async (data) => {
    const command = <string>data.command
    const event_name = <string>data.event_name

    logseq.Editor.registerSlashCommand(command, async (_) => {
      socket.emit(event_name)
    })
    console.log("Registered slash command:", command, event_name)
  })

  socket.on("Editor.registerBlockContextMenuItem", async (data) => {
    const tag = <string>data.tag
    const event_name = <string>data.event_name

    logseq.Editor.registerBlockContextMenuItem(tag, async (...args) => {
      console.log("Block context menu item clicked:", tag, event_name, args)
      socket.emit(event_name)
    })
    console.log("Registered block context menu item:", tag, event_name)
  })

  socket.on("Editor.onInputSelectionEnd", async (data) => {
    const event_name = <string>data.event_name

    logseq.Editor.onInputSelectionEnd(async (e) => {
      console.log("Input selection end:", event_name, e)
      socket.emit(event_name, e)
    })
    console.log("Registered input selection end:", event_name)
  })

  async function executeFunctionByName(functionName, context, args) {
    var namespaces = functionName.split(".");
    var func = namespaces.pop();
    console.log("Executing function:", namespaces, func, args, context)
    for (var i = 0; i < namespaces.length; i++) {
      context = context[namespaces[i]];
    }
    // If func is AsyncFunction, then call it with await, else call it normally
    if (context[func].constructor.name === "AsyncFunction") {
      console.log("Calling async function")
      if (args.length > 0) {
        return await context[func].apply(context, args);
      } else {
        return await context[func].apply(context);
      }
    } else {
      console.log("Calling function")
      if (args.length > 0) {
        return context[func].apply(context, args);
      } else {
        return context[func].apply(context);
      }
    }
  }

  socket.onAny(async (event, data, callback) => {
    var args = <string[]>data.args
    // take all key, value pairs in data except args
    var opts = Object.assign({}, data)
    delete opts.args
    args.push(opts)

    // Skip existing handlers
    if ([
      "connect",
      "disconnect",
      "useSettingsSchema",
      "Editor.registerSlashCommand",
      "Editor.registerBlockContextMenuItem",
      "Editor.onInputSelectionEnd",
    ].includes(event)) {
      console.log("Skipping event:", event)
      return
    }
    const current_page = await logseq.App.getCurrentPage()
    console.log({current_page})
    console.log("Received event:", event, args)
    var result: any
    try {
      console.log("Executing event:", event, args)
      result = await executeFunctionByName(event, logseq, args)
      console.log("Result:", result)
      if (callback && result) {
        console.log("Calling callback with result:", result)
        callback(result)
      } else if (callback) {
        console.log("Calling callback with 'null'")
        callback("null")
      }
    } catch (e) {
      console.error("Error executing function:", event, e)
      result = e
      if (callback) {
        console.log("Calling callback with result:", result)
        callback(result)
      }
    }
  })

  console.log("Plugin: loaded.")
}

logseq.ready(main).catch(console.error)
