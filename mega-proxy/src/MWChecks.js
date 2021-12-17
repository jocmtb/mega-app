
window.axios = require("axios");
window.axios.defaults.headers.common["X-Requested-With"] = "XMLHttpRequest";
Vue.prototype.$axios = axios;

import vSelect from "vue-select";
import "vue-select/dist/vue-select.css";
Vue.component("v-select", vSelect);

var app = new Vue({
    el: "#app",
    delimiters: ['[[', ']]'],
    data() {
        return {
            report:{
                id_claro:'',
                description:'',
                class_mw:'***',
                configuration: []
            },
            devices_search:'',
            controls: [],
            runNow: true,
            options: [],
            commandOptions:[],
            copy:null
        };
    },
    computed: {
        configuration() {
            return JSON.stringify(this.report.configuration)
        }
    },
    mounted() {
    },
    updated() {
    },
    methods: {
        copyConf(index){
            this.copy = this.report.configuration[index].commands;
        },
        pasteConf(index){
            if(this.copy){
                for(let i in this.copy){
                    this.report.configuration[index].commands.push(this.copy[i]);
                }
            }
            this.copy = null;
        },
        getDevices(search) {
            this.$axios
                .get(`/mwChecks/devices_search?q=${escape(search)}`)
                .then((res) => {
                    this.options = [];
                    for(let i in res.data.options){
                        let added = this.report.configuration.filter((e) => e.hostname == res.data.options[i].code).length;
                        if(!added){
                            this.options.push(res.data.options[i]);
                        }
                    }
                });
        },
        getCommands(search,index) {
            this.$axios
                .get(`/mwChecks/commands_search?q=${escape(search)}`)
                .then((res) => {
                    this.commandOptions = [];
                    for(let i in res.data.options){
                        let added = this.report.configuration[index].commands.filter((e) => e == res.data.options[i].code).length;
                        if(!added){
                            this.commandOptions.push(res.data.options[i]);
                        }
                    }
                });
        },
        addDevice(event){
            if(event.type == 'tag'){
                this.$axios
                .get(`/mwChecks/get_devices_by_tag/${escape(event.code)}`)
                .then((res) => {
                    for(let i in res.data.devices){
                        this.report.configuration.push({
                            'hostname': res.data.devices[i],
                            'commands': []
                        });
                        this.controls.push({val:''});
                    }
                }); 
            }else{
                this.report.configuration.push({
                    'hostname': event.code,
                    'commands': []
                });
                this.controls.push({val:''});
            }
            this.devices_search = '';
        },
        addCommand(event,index){
            if(event.type == 'tag'){
                this.$axios
                .get(`/mwChecks/get_commands_by_tag/${escape(event.code)}`)
                .then((res) => {
                    for(let i in res.data.commands){
                        this.report.configuration[index].commands.push(res.data.commands[i]);
                    }
                }); 
            }else{
                this.report.configuration[index].commands.push(event.code)
            }
            this.controls[index].val = '';
        },
        removeDevice(i){
            this.report.configuration.splice(i,1);
        },
        removeCommand(i,j){
            this.report.configuration[i].commands.splice(j,1);
        }
    }
  });
  
  
   