import '@logseq/libs';
import { BlockEntity, SettingSchemaDesc } from '@logseq/libs/dist/LSPlugin';
import * as io from "socket.io-client";

const settingsSchema: SettingSchemaDesc[] = [
    {
        key: "pluginServerURL",
        type: "string",
        default: "http://localhost:8484/",
        title: "Plugin URL",
        description: "Python Plugin URL. Default: http://localhost:8484/",
    },
]

async function main() {
    logseq.useSettingsSchema(settingsSchema);
    var errors = 0
    var _commands_registered: string[] = []
    var _shortcuts_registered: string[] = []
    var _menuitems_registered: string[] = []

    const PLUGIN_SERVER_URL = logseq.settings!["pluginServerURL"]
    if (!PLUGIN_SERVER_URL) {
        logseq.App.showMsg('Python Plugin requires pluginServerURL. Please configure in plugin settings.', 'error')
        console.log('logseq-python-plugin: Error: pluginServerURL required, please configure in settings.')
        errors += 1
    }

    if (errors > 0) {
        console.log(`logseq-python-plugin: Encountered ${errors} errors, exiting.`)
        logseq.showSettingsUI()
        return
    }

    const socket = io.connect(`${PLUGIN_SERVER_URL}`, {
        transports: ["websocket"]
    });

    socket.on('connect', async () => {
        console.log('logseq-python-plugin: Connected');
        socket.emit("plugin_loaded")
    });

    socket.on("logseq.useSettingsSchema", async (settings, callback) => {
        console.log("logseq.useSettingsSchema", settings)
        const settings_schema = <SettingSchemaDesc[]>settings
        logseq.useSettingsSchema(settings_schema);
        callback(logseq.settings)
    })

    socket.on("logseq.App.showMsg", async (message: string, type: string) => {
        logseq.App.showMsg(message, type)
    })

    socket.on("logseq.Editor.registerSlashCommand", async (command: string, event_name: string) => {
        if (_commands_registered.includes(command)) {
            console.log("logseq-telegram-plugin: Command: ", command, " for event name: ", event_name, "exists.")
        } else {
            console.log("logseq-telegram-plugin: Register command: ", command, " for event name: ", event_name)
            logseq.Editor.registerSlashCommand(command, async () => {
                socket.emit(event_name)
            })
            _commands_registered.push(command)
        }
    })

    socket.on("logseq.Editor.registerCommandPalette", async (label: string, shortcut: string, event_name: string) => {
        if (_shortcuts_registered.includes(shortcut)) {
            console.log("logseq-telegram-plugin: Keyboard shortcut: ", shortcut, " for event name: ", event_name, "exists.")
        } else {
            console.log("logseq-telegram-plugin: Register keyboard shortcut: ", shortcut, " for event name: ", event_name)
            logseq.App.registerCommandPalette({
                key: `custom-shortcut-${shortcut}`,
                label: label,
                keybinding: {
                    mode: 'global',
                    binding: shortcut
                }
            }, () => {
                socket.emit(event_name)
            })
            _shortcuts_registered.push(shortcut)
        }
    })

    socket.on("logseq.Editor.registerBlockContextMenuItem", async (item_name: string, event_name: string) => {
        if (_menuitems_registered.includes(item_name)) {
            console.log("logseq-telegram-plugin: Menu item: ", item_name, " for event name: ", event_name, "exists.")
        } else {
            console.log("logseq-telegram-plugin: Menu item: ", item_name, " for event name: ", event_name)
            logseq.Editor.registerBlockContextMenuItem(item_name, async (e) => {
                socket.emit(event_name, e)
            })
            _menuitems_registered.push(item_name)
        }
    })

    socket.on("logseq.Editor.insertAtEditingCursor", async (content: string) => {
        await logseq.Editor.insertAtEditingCursor(content)
    })

    socket.on("logseq.Editor.getEditingBlockContent", async (callback) => {
        const content = await logseq.Editor.getEditingBlockContent()
        callback(content)
    })

    socket.on("logseq.Editor.getCurrentBlock", async (callback) => {
        const block = await logseq.Editor.getCurrentBlock()
        callback(block)
    })

    socket.on("logseq.Editor.getPage", async (page_name: string, callback) => {
        const page = await logseq.Editor.getPage(page_name)
        callback(page)
    })

    socket.on("logseq.Editor.getPageBlocksTree", async (page_name: string, callback) => {
        const page = await logseq.Editor.getPageBlocksTree(page_name)
        callback(page)
    })

    socket.on("logseq.Editor.getBlock", async (kwargs, callback) => {
        const page = await logseq.Editor.getBlock(kwargs.srcBlock, { includeChildren: kwargs.includeChildren })
        callback(page)
    })

    socket.on("logseq.Editor.openInRightSidebar", async (uuid: string) => {
        logseq.Editor.openInRightSidebar(uuid)
    })

    socket.on("logseq.Editor.insertBlock", async (kwargs, callback) => {
        const block = await logseq.Editor.insertBlock!(kwargs.srcBlock, kwargs.content, { properties: kwargs.properties, before: kwargs.before, sibling: kwargs.sibling, isPageBlock: kwargs.isPageBlock })
        callback(block)
    })

    socket.on("logseq.Editor.updateBlock", async (kwargs, callback) => {
        console.log("logseq-telegram-plugin: updateBlock", kwargs)
        const block = await logseq.Editor.updateBlock(kwargs.srcBlock, kwargs.content, { properties: kwargs.properties })
        console.log("logseq-telegram-plugin: updateBlock", block)
        callback({ block: block })
    })

    socket.on("logseq.Editor.upsertBlockProperty", async (srcBlock, key, value) => {
        await logseq.Editor.upsertBlockProperty(srcBlock, key, value)
    })

    logseq.Editor.onInputSelectionEnd(async (e) => {
        socket.emit("logseq.Editor.onInputSelectionEnd", e)
    })


    socket.on("logseq.DB.datascriptQuery", async (query: string, callback) => {
        const d = new Date();
        const todayDateObj = {
            day: `${d.getDate()}`.padStart(2, "0"),
            month: `${d.getMonth() + 1}`.padStart(2, "0"),
            year: d.getFullYear(),
        };
        const todayDate = `${todayDateObj.year}${todayDateObj.month}${todayDateObj.day}`;
        console.log("logseq-python-plugin: Running datascript query: ", query)
        console.log("logseq-python-plugin: Today date: ", todayDate)
        const result = await logseq.DB.datascriptQuery(query)
        callback(result)
    })


    console.info("logseq-python-plugin: Loaded")
}

function display_error(e) {
    console.error(e)
}

logseq.ready(main).catch(display_error)
