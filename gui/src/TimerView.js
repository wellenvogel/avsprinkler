import React, { Component } from 'react';
import ToolBar from './components/ToolBar';
import IconButton from 'react-toolbox/lib/button';
import TimerEntry from './components/TimerEntry';
import {List} from 'react-toolbox/lib/list';


const urlbase="/control";
class TimerView extends Component {

    constructor(props){
        super(props);
        this.state=props;
        this.goBack=this.goBack.bind(this);
        this.fetchStatus=this.fetchStatus.bind(this);
        this.onItemClick=this.onItemClick.bind(this);
    }
    fetchStatus(){
        let self=this;
        fetch(urlbase+"?request=status",{
            credentials: 'same-origin'
        }).then(function(response){
            if (! response.ok){
                alert("Error: "+response.statusText);
                throw new Error(response.statusText)
            }
            return response.json()
        }).then(function(jsonData){
            self.setState(jsonData||{});
        })
    }
    runCommand(text,url){
        let self=this;
        fetch(url,{
            credentials: 'same-origin'
        }).then(function(response){
            if (! response.ok){
                alert("Error: "+response.statusText);
                throw new Error(response.statusText)
            }
            return response.json()
        }).then(function(jsonData){
            if (jsonData.status !== 'OK'){
                alert(text+" failed: "+jsonData.info);
            }else{
                self.fetchStatus();
            }
        })
    }
    getChannel(){
        let ch=this.props.match.params.channel||1;
        if (ch !== undefined) return parseInt(ch);
    }
    getChannelInfo(channel){
        if (! this.state.data) return;
        let channels=this.state.data.channels.outputs;
        if (! channels) return;
        for (let i=0;i<channels.length;i++){
            let cdata=channels[i];
            if (cdata.channel === channel) return cdata;
        }
    }
    getTimers(channel){
        if (! this.state.data) return;
        let tlist=this.state.data.timer.entries;
        if (! tlist) return;
        let rt=[];
        for (let i=0;i<tlist.length;i++){
            let te=tlist[i];
            if (te.channel === channel) rt.push(te)
        }
        return rt;
    }
    componentDidMount(){
        let self=this;
        this.interval=setInterval(this.fetchStatus,2000);
        this.fetchStatus();
    }
    componentWillUnmount(){
        clearInterval(this.interval);
    }
    render() {
        let self=this;
        let info=this.state;
        let title=info.title||"TimerView";
        if (info.data){
            let cinfo=this.getChannelInfo(this.getChannel())
            if (cinfo){
                title=cinfo.name
            }
        }
        let timers=this.getTimers(this.getChannel());
        return (
            <div className="view timerView">
                <ToolBar leftIcon="arrow_back"
                    leftClick={this.goBack}>
                    <span className="toolbar-label">{title}</span>
                    <span className="spacer"/>
                </ToolBar>
                <div className="mainDiv">
                    <List>
                        {timers ?
                            timers.map(function (te) {
                                return <TimerEntry {...te} onItemClick={self.onItemClick}/>
                            })
                            :
                            <p>Loading...</p>
                        }
                    </List>
                </div>
            </div>
        );
    }
    goBack(){
        this.props.history.goBack();
    }
    onItemClick(te){
        console.log("item click");
    }
}


export default TimerView;
