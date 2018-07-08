import React, { Component } from 'react';
import ToolBar from './components/ToolBar';
import IconButton from 'react-toolbox/lib/button';
import {List} from 'react-toolbox/lib/list';
import ChannelItem from './components/ChannelItem';
import Dialog from 'react-toolbox/lib/dialog';

const urlbase="/control";
class ExampleView extends Component {

    constructor(props){
        super(props);
        this.state=props;
        this.onStart=this.onStart.bind(this);
        this.onStop=this.onStop.bind(this);
        this.fetchStatus=this.fetchStatus.bind(this);
        this.durationChange=this.durationChange.bind(this);
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
                self.runCommand("start",urlbase+"?request=start&channel="+self.state.channel+"&duration="+(self.state.duration||15)*60);
                self.setState({dialogVisible:false});
            }}
        ];
        let title=info.title||"Sprinkler";
        if (! info.data){
            return (<p>Loading...</p>);
        }
        return (
            <div className="view exampleView">
                <ToolBar >
                    <span className="toolbar-label">{title}</span>
                </ToolBar>
                <div className="mainDiv">
                    <List>
                        {info.data.channels.outputs.map(function(x){
                            let props={
                                name:x.name,
                                id:x.channel,
                                time:x.accumulatedTime,
                                count: x.accumulatedCount,
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
                                        props.count=info.data.controller.meter-cc.startCount||0;
                                    }
                                }
                            }
                        return <ChannelItem {...props} />
                    })}
                    </List>
                </div>
                <Dialog actions={dialogActions}
                active={this.state.dialogVisible}
                title={"Starte Kanal "+self.state.channel}>
                    <p>Laufzeit(Minuten)</p>
                    <input type="number"  value={self.state.duration||15} onChange={self.durationChange}/>
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

}


export default ExampleView;
