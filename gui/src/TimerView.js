import React, { Component } from 'react';
import ToolBar from './components/ToolBar';
import {Button,IconButton} from 'react-toolbox/lib/button';
import TimerEntry from './components/TimerEntry';
import {List} from 'react-toolbox/lib/list';
import ButtonTheme from './style/theme/fabButton.less';
import TimerDialog from './components/TimerEdit';
import Util from './components/Util.js';


const urlbase="/control";
class TimerView extends Component {

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
        let self=this;
        if (! this.state.data) return;
        let tlist=this.state.data.timer.entries;
        if (! tlist) return;
        let rt=[];
        for (let i=0;i<tlist.length;i++){
            let te=tlist[i];
            if (te.channel === channel) rt.push(te)
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
    render() {
        let self=this;
        let info=this.state;
        let title=info.title||"TimerView";
        if (info.data){
            let cinfo=this.getChannelInfo(this.getChannel());
            if (cinfo){
                title="Timer "+cinfo.name
            }
        }
        let timers=this.getTimers(this.getChannel());
        let dialogProps={
            dialogVisible:this.state.dialogVisible,
            dialogChannel:this.getChannel(),
            dialogStart: this.state.dialogStart,
            dialogWeekday: this.state.dialogWeekday,
            dialogDuration: this.state.dialogDuration,
            dialogTimerId: this.state.dialogTimerId,
            hideCallback: this.hideDialog,
            callback: function(tp){self.setState({dialogDuration:tp.dialogDuration});self.fetchStatus();}

        };
        return (
            <div className="view timerView">
                <ToolBar leftIcon="arrow_back"
                         leftClick={this.goBack}>
                    <span className="toolbar-label">{title}</span>
                    <span className="spacer"/>
                    <span className="rightButtons">
                        <IconButton icon="history" onClick={function() {self.props.history.push("/history/"+self.getChannel());}}/>
                        <IconButton icon="timer" onClick={function() {self.props.history.push("/timerlist/");}}/>
                    </span>
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
                <Button icon="add" floating primary onClick={this.onPlus} className="plusButton" theme={ButtonTheme}/>
                {this.state.dialogVisible ?
                    <TimerDialog {...dialogProps}></TimerDialog>
                    :
                    null
                }

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
            dialogActions:this.dialogEditActions
        });
    }
    onPlus(){
        this.setState({
            dialogVisible:true,
            dialogTimerId:0,
            dialogWeekday:0,
            dialogStart:"06:00",
            dialogDuration:this.state.dialogDuration||20,
            dialogActions:this.dialogNewActions
        });
    }
}


export default TimerView;
