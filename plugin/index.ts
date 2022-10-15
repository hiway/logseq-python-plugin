import '@logseq/libs'
import { SettingSchemaDesc, SimpleCommandKeybinding } from '@logseq/libs/dist/LSPlugin';
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

  socket.on("App.onBlockRendererSlotted", async (data) => {
    const event_name = <string>data.event_name

    logseq.App.onBlockRendererSlotted(async (e) => {
      console.log("Block renderer slotted:", event_name, e)
      socket.emit(event_name, e)
    })
    console.log("Registered block renderer slotted:", event_name)
  })

  socket.on("App.onCurrentGraphChanged", async (data) => {
    const event_name = <string>data.event_name
    logseq.App.onCurrentGraphChanged(
      async (e) => {
        console.log("Current graph changed:", event_name, e)
        const graph = await logseq.App.getCurrentGraph()
        socket.emit(event_name, graph)
      },
    )
    console.log("Registered current graph changed:", event_name)
  })

  socket.on("App.onMacroRendererSlotted", async (data) => {
    const event_name = <string>data.event_name

    // @ts-ignore
    logseq.App.onMacroRendererSlotted(async ({ slot, payload: { arguments } }) => {
      console.log("Macro renderer slotted:", event_name, slot, arguments)
      socket.emit(event_name, { slot, arguments })
    })
    console.log("Registered macro renderer slotted:", event_name)
  })

  socket.on("App.onPageHeadActionsSlotted", async (data) => {
    const event_name = <string>data.event_name

    logseq.App.onPageHeadActionsSlotted(async (e) => {
      console.log("Page head actions slotted:", event_name, e)
      socket.emit(event_name, e)
    })
    console.log("Registered page head actions slotted:", event_name)
  })

  socket.on("App.onRouteChanged", async (data) => {
    const event_name = <string>data.event_name

    logseq.App.onRouteChanged(async (e) => {
      console.log("Route changed:", event_name, e)
      socket.emit(event_name, e)
    })
    console.log("Registered route changed:", event_name)
  })

  socket.on("App.onSidebarVisibleChanged", async (data) => {
    const event_name = <string>data.event_name

    logseq.App.onSidebarVisibleChanged(async (e) => {
      console.log("Sidebar visible changed:", event_name, e)
      socket.emit(event_name, e)
    })
    console.log("Registered sidebar visible changed:", event_name)
  })

  socket.on("App.onThemeModeChanged", async (data) => {
    const event_name = <string>data.event_name

    logseq.App.onThemeModeChanged(async (e) => {
      console.log("Theme mode changed:", event_name, e)
      socket.emit(event_name, e)
    })
    console.log("Registered theme mode changed:", event_name)
  })

  socket.on("App.registerCommand", async (data) => {
    // registerCommand(type: string, opts: { desc?: string; key: string; keybinding?: SimpleCommandKeybinding; label: string; palette?: boolean }, action: SimpleCommandCallback): void
    const type = <string>data.type
    const desc = <string>data.desc
    const key = <string>data.key
    const keybinding = <SimpleCommandKeybinding>data.keybinding
    const label = <string>data.label
    const palette = <boolean>data.palette
    const event_name = <string>data.event_name

    logseq.App.registerCommand(type, { desc, key, keybinding, label, palette }, async (e) => {
      console.log("Command registered:", type, desc, key, keybinding, label, palette, event_name, e)
      socket.emit(event_name, e)
    })
    console.log("Registered command:", type, desc, key, keybinding, label, palette, event_name)
  })
  
  socket.on("App.registerCommandPalette", async (data) => {
    // registerCommandPalette(opts: { key: string; keybinding?: SimpleCommandKeybinding; label: string }, action: SimpleCommandCallback): void
    const key = <string>data.key
    const keybinding = <SimpleCommandKeybinding>data.keybinding
    const label = <string>data.label
    const event_name = <string>data.event_name

    logseq.App.registerCommandPalette({ key, keybinding, label }, async (e) => {
      console.log("Command palette registered:", key, keybinding, label, event_name, e)
      socket.emit(event_name, e)
    })
    console.log("Registered command palette:", key, keybinding, label, event_name)
  })
  
  // socket.on("DB.onBlockChanged", async (data) => {
  //   // onBlockChanged(uuid: string, callback: (block: BlockEntity, txData: IDatom[], txMeta?: { outlinerOp: string }) => void): IUserOffHook
  //   const event_name = <string>data.event_name
  //   const uuid = <string>data.uuid

  //   logseq.DB.onBlockChanged(uuid, async (block, txData, txMeta) => {
  //     console.log("Block changed:", event_name, {"uuid":uuid, "block":block, "txData":txData, "txMeta":txMeta})
  //     socket.emit(event_name, {"uuid":uuid, "block":block, "txData":txData, "txMeta":txMeta})
  //   })
  //   console.log("Registered block changed:", event_name, uuid)
  // })

  // socket.on("DB.onChanged", async (data) => {
  //   // onChanged: IUserHook<{ blocks: BlockEntity[]; txData: IDatom[]; txMeta?: { outlinerOp: string } }, IUserOffHook>
  //   const event_name = <string>data.event_name

  //   logseq.DB.onChanged(async (e) => {
  //     console.log("DB changed:", event_name, e)
  //     socket.emit(event_name, e)
  //   })
  //   console.log("Registered DB changed:", event_name)
  // })

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
      "App.onBlockRendererSlotted",
      "App.onCurrentGraphChanged",
      "App.onMacroRendererSlotted",
      "App.registerCommand",
      "App.registerCommandPalette",
      "DB.onChanged",
      "DB.onBlockChanged",
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
