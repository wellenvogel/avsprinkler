import React, { Component } from 'react';
import ToolBar from './components/ToolBar';
import Button from 'react-toolbox/lib/button';
import TimerEntry from './components/TimerEntry';
import {List} from 'react-toolbox/lib/list';
import ButtonTheme from './style/theme/fabButton.less';
import TimerDialog from './components/TimerEdit';
import Util from './components/Util.js';


const urlbase="/control";
class TimerListView extends Component {

    constructor(props){
        super(props);
        this.state=props;
        this.goBack=this.goBack.bind(this);
        this.fetchStatus=this.fetchStatus.bind(this);
        this.onItemClick=this.onItemClick.bind(this);
        this.onPlus=this.onPlus.bind(this);
        this.hideDialog=this.hideDialog.bind(this);
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
    getChannelInfo(channel){
        if (! this.state.data) return;
        let channels=this.state.data.channels.outputs;
        if (! channels) return;
        for (let i=0;i<channels.length;i++){
            let cdata=channels[i];
            if (cdata.channel === channel) return cdata;
        }
    }
    getTimers(){
        let self=this;
        if (! this.state.data) return;
        let tlist=this.state.data.timer.entries;
        if (! tlist) return;
        let rt=[];
        for (let i=0;i<tlist.length;i++){
            let te=tlist[i];
            rt.push(te)
        }
        rt.sort(Util.timerSort);
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
    getChannelDisplayList(){
        if (! this.state.data) return;
        let channels=this.state.data.channels.outputs;
        if (! channels) return;
        let rt=[];
        for (let i=0;i<channels.length;i++){
            rt.push({label:channels[i].name,value:channels[i].channel})
        }
        return rt;
    }
    render() {
        let self=this;
        let info=this.state;
        let title="Timer Liste";
        let timers=this.getTimers();
        let dialogProps={
            dialogVisible:this.state.dialogVisible,
            dialogChannel:this.state.dialogChannel,
            dialogStart: this.state.dialogStart,
            dialogWeekday: this.state.dialogWeekday,
            dialogDuration: this.state.dialogDuration,
            dialogTimerId: this.state.dialogTimerId,
            dialogTitle: this.state.dialogTitle,
            hideCallback: this.hideDialog,
            callback: function(tp){
                self.setState({
                    dialogChannel:tp.dialogChannel,
                    dialogDuration: tp.dialogDuration,
                    dialogStart: tp.dialogStart,
                    dialogWeekday: tp.dialogWeekday
                    });
                self.fetchStatus();
            },
            channelSelector: this.state.dialogChannelList
        };
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
                                let ti=self.getChannelInfo(te.channel);
                                return <TimerEntry {...te}  channelName={ti.name} timerEnabled={ti.timerEnabled} onItemClick={self.onItemClick}/>
                            })
                            :
                            <p>Loading...</p>
                        }
                    </List>
                </div>
                {this.state.dialogVisible ?
                    <TimerDialog {...dialogProps}></TimerDialog>
                    :
                    null
                }
                <Button icon="add" floating primary onClick={this.onPlus} className="plusButton" theme={ButtonTheme}/>

            </div>
        );
    }
    hideDialog(){
        this.setState({dialogVisible:false});
    }
    goBack(){
        this.props.history.goBack();
    }
    onItemClick(te){
        this.setState({
            dialogVisible:true,
            dialogTimerId:te.id,
            dialogWeekday:te.weekday,
            dialogStart:te.start,
            dialogDuration:te.duration,
            dialogChannel:te.channel,
            dialogActions:this.dialogEditActions,
            dialogTitle:this.getChannelInfo(te.channel).name
        });
    }
    onPlus(){
        let channelList=this.getChannelDisplayList();
        if (! channelList) return;
        this.setState({
            dialogVisible:true,
            dialogTimerId:undefined,
            dialogWeekday:this.state.dialogWeekday||0,
            dialogStart:this.state.dialogStart||"06:00",
            dialogDuration:this.state.dialogDuration||15,
            dialogActions:this.dialogNewActions,
            dialogChannelList: channelList
        });
    }
}


export default TimerListView;
