import React, { Component } from 'react';
import ToolBar from './components/ToolBar';
import {List} from 'react-toolbox/lib/list';
import ChannelItem from './components/ChannelItem';
import Dialog from 'react-toolbox/lib/dialog';
import {ListItem} from "react-toolbox/lib/list";
import {Button, IconButton} from 'react-toolbox/lib/button';
import TimerSwitchTheme from './style/theme/timerSwitch.less';
import dialogTheme from './style/theme/dialog.less';
import assign from 'object-assign';

const urlbase="/control";
class ExampleView extends Component {

    constructor(props){
        super(props);
        this.state=assign({},props,{duration:20});
        this.onStart=this.onStart.bind(this);
        this.onStop=this.onStop.bind(this);
        this.fetchStatus=this.fetchStatus.bind(this);
        this.durationChange=this.durationChange.bind(this);
        this.onItemClick=this.onItemClick.bind(this);
        this.startTimers=this.startTimers.bind(this);
        this.stopTimers=this.stopTimers.bind(this);
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
    componentDidMount(){
        this.interval=setInterval(this.fetchStatus,2000);
        this.fetchStatus();
    }
    componentWillUnmount(){
        clearInterval(this.interval);
    }
    render() {
        let self=this;
        let info=this.state;
        let dialogActions=[
            {label:"Abbrechen",onClick: function(){self.setState({dialogVisible:false})}},
            {label:"OK",onClick: function(){
                self.runCommand("start",urlbase+"?request=start&channel="+self.state.channel+"&duration="+(self.state.duration||20)*60);
                self.setState({dialogVisible:false});
            }}
        ];
        let title=info.title||"Sprinkler";
        if (! info.data){
            return (<p>Loading...</p>);
        }
        let TimerSwitch=function(props) {
            return (<ListItem caption="Timer Automatik" className="timerSwitch" theme={TimerSwitchTheme} legend={props.sum+"l"}>
                {props.active?
                    <Button label="Stop" raised className="buttonStop" onClick={self.stopTimers}/>
                    :
                    <Button label="Start" raised className="buttonStart" onClick={self.startTimers}/>

                }
            </ListItem>);
        };
        return (
            <div className="view exampleView">
                <ToolBar >
                    <span className="toolbar-label">{title}</span>
                    <span className="rightButtons">
                        <IconButton icon="history" onClick={function() {self.props.history.push("/history/");}}/>
                        <IconButton icon="timer" onClick={function() {self.props.history.push("/timerlist/");}}/>
                    </span>
                </ToolBar>
                <div className="mainDiv">
                    <List>
                        <TimerSwitch active={info.data.timer.running} sum={Math.round(info.data.controller.meter/info.data.controller.ppl||1)}/>
                        {info.data.channels.outputs.map(function(x){
                            let timerSum=0;
                            let timerNumber=0;
                            info.data.timer.entries.forEach(function(timer){
                                if (timer.channel===x.channel){
                                    timerSum+=timer.duration;
                                    timerNumber+=1;
                                }
                            });
                            let props={
                                name:x.name,
                                id:x.channel,
                                time:x.accumulatedTime,
                                count: x.accumulatedCount,
                                timerEnabled: x.timerEnabled,
                                timerSum: timerSum,
                                timerNumber:timerNumber,
                                onStart: self.onStart,
                                onStop: self.onStop,
                                onItemClick: self.onItemClick
                            };
                            if (info.data.controller.status === 'on'){
                                if (info.data.controller.channel){
                                    let cc=info.data.controller.channel;
                                    if (cc.id === x.channel){
                                        props.active=true;
                                        props.start=new Date(cc.started*1000);
                                        props.running=cc.running;
                                        props.remain=cc.remain;
                                        props.runtime=cc.runtime;
                                        props.ccount=info.data.controller.meter-cc.startCount||0;
                                    }
                                }
                            }
                            props.ppl=info.data.controller.ppl;
                        return <ChannelItem {...props} />
                    })}
                    </List>
                </div>
                <Dialog actions={dialogActions} theme={dialogTheme}
                active={this.state.dialogVisible}
                title={"Starte Kanal "+self.state.channel}>
                    <p>Laufzeit(Minuten)</p>
                    <input type="number"  value={self.state.duration||20} onChange={self.durationChange}/>
                </Dialog>

            </div>
        );
    }
    durationChange(ev){
        this.setState({duration:ev.target.value});
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
    onStart(channel){
        this.setState({
            channel:channel,
            dialogVisible:true
        });
    }
    onStop(channel){
        this.runCommand("stop",urlbase+"?request=stop");
    }
    onItemClick(channel){
        this.props.history.push("/timer/"+channel);
    }
    stopTimers(){
        this.runCommand("stop timers",urlbase+"?request=stopTimers");
    }
    startTimers(){
        this.runCommand("start timers",urlbase+"?request=startTimers");
    }

}


export default ExampleView;
