// TODO stop threads on exit

function isJson(str) { // this is from stackoverflow idk
    try {
        let obj = JSON.parse(str);
        if (obj && typeof obj === "object"){
             return true;
        }
    } catch (e) {
        return false;
    }
    return true;
}

// Returns a filename that is safe, replaces bad chars with another one
function safeFilename(filename, char){
    return filename
        .replace('\\', char).replace('/', char).replace(':', char)
        .replace('*', char).replace('?', char).replace('"', char)
        .replace('<', char).replace('>', char).replace('|', char)
}


function paramsToJsonString(...params){  //transform terminal params into a json string
    let outputJSON = {"params": []}
    params.forEach(param => {
        outputJSON["params"].push(param)
    })
    return JSON.stringify(outputJSON)
}


function download(filename, text) {  // download a file
    let element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}


const defaultPrompt = '> '
const loading_animation = ['   ', '.  ', '.. ', '...', ' ..', '  .']

const terminal = $('body').terminal({
    "help": function(){
        this.echo('\nAvailable commands')
        this.echo(' [[;#00cccc;]hashcash6]    Runs the hashcash6 script')
        this.echo(' cls          Clears the console')
        this.echo(' help         Displays this message')
        this.echo(' latency      Returns the latency between server and front-end')
        this.echo()
    },
    "latency": async function () {
        this.pause(true)

        const requestStartTime = new Date(); //start time

        let i = 1
        terminal.set_prompt('   ')
        let loadingPromptAnimation = window.setInterval(function () {
            terminal.set_prompt(loading_animation[i])
            i = (i + 1) % loading_animation.length
        }, 350);

        const hasResponded = await fetch('_ping', {method: 'GET'})
            .then((response)=>{
                clearInterval(loadingPromptAnimation)
                this.set_prompt(defaultPrompt)
                return true
            })

        this.echo(`[[i;;]${new Date()-requestStartTime}ms`)
        this.resume()
    },
    "cls": function(){
        this.clear()
    },
    "hashcash6": async function (...params) {
        this.pause(true)

        const requestStartTime = new Date(); //start time

        const jsonStringParams = paramsToJsonString(params)

        let i = 1
        terminal.set_prompt('   ')
        let loadingPromptAnimation = window.setInterval(function () {
            terminal.set_prompt(loading_animation[i])
            i = (i + 1) % loading_animation.length
        }, 350);

        const response_text = await fetch('_parse_params', {method: 'POST', body: jsonStringParams})
            .then((response) => {
                clearInterval(loadingPromptAnimation)
                this.set_prompt(defaultPrompt)
                return response.text()
            })

        if (isJson(response_text)) {    // We got a hashcash calculation result
            let response = JSON.parse(response_text)
            const header = response['header']
            const threads = response['threads']
            const resource = response['resource']
            const zeroBits = response['zero_bits']
            const timeElapsed = response['time_elapsed']
            const hashBin = response['hash_bin']
            const hashHex = response['hash_hex']

            this.echo(`\n[[;green;]Generated Hashcash6 for "${resource}" with [[;#ac98b8;]${zeroBits} zero bits] using ${threads} threads]\n`)

            this.echo(`[[gb;#00cccc;]X-Hashcash]: [[;#aaaaaa;black]${header}]\n`)
            this.echo(`[[gb;#00cccc;]Hash (HEX)]: ${hashHex}\n`)
            this.echo(`[[gb;#00cccc;]Hash (BIN)]: [[;#ac98b8;]${hashBin.substring(0, zeroBits)}]${hashBin.substring(zeroBits)}\n`)
            this.echo(`[[i;;]Hashcash6 calculation took ${timeElapsed}`)
            this.echo(`[[i;;]Got response from server after ${new Date()-requestStartTime}ms`)

            if (jsonStringParams.includes('--download')) {
                const timestamp = header.split(':')[2]
                download(
                    safeFilename(`${timestamp}_${resource}.json`, '_'),
                    JSON.stringify(response, null, '\t')
                )
            }
            this.echo()
        } else {  // we got another kind of output from the cli
            this.echo(response_text)
        }
        this.resume()
    }
}, {
    softPause: true,
    autocompleteMenu: true,
    completion: function(string, callback) {
        if (this.get_command().match(/^hashcash6 /)) {
            callback(['--zero-bits', '--len-rand', '--len-counter', '--threads', '--download', '--about', '--help']);
        } else {
            callback(['hashcash6', 'help', 'latency', 'cls']);
        }
    },
    checkArity:false,
    greetings: 'Welcome to Hashcash6, to get started use the [[;#00cccc;]"hashcash6 --help"] command.',
    keymap: {
        'CTRL+C': function() {} // Disable CTRL+C
    }
},
);

// If it's the first time the user visits the page, run the hashcash6 --about command
const firstTime = localStorage.getItem("first_time");
if(!firstTime) {
    terminal.exec('hashcash6 --about')
    localStorage.setItem("first_time","1");
}