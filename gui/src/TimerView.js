import React, { Component } from 'react';
import ToolBar from './components/ToolBar';
import Button from 'react-toolbox/lib/button';
import TimerEntry from './components/TimerEntry';
import {List} from 'react-toolbox/lib/list';
import ButtonTheme from './style/theme/fabButton.less';
import Dialog from 'react-toolbox/lib/dialog';
import {RadioGroup,RadioButton} from 'react-toolbox/lib/radio';
import Util from './components/Util';
import RadioTheme from './style/theme/radioButton.less';


const urlbase="/control";
class TimerView extends Component {

    constructor(props){
        super(props);
        this.state=props;
        this.goBack=this.goBack.bind(this);
        this.fetchStatus=this.fetchStatus.bind(this);
        this.onItemClick=this.onItemClick.bind(this);
        this.onPlus=this.onPlus.bind(this);
        this.vchange=this.vchange.bind(this);
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
    addParametersToUrl(url){
       url+="channel="+encodeURIComponent(this.getChannel());
       url+="&start="+encodeURIComponent(this.state.dialogStart);
       url+="&weekday="+encodeURIComponent(this.state.dialogWeekday);
       url+="&duration="+encodeURIComponent(this.state.dialogDuration);
       return url;
    }
    componentDidMount(){
        let self=this;
        this.interval=setInterval(this.fetchStatus,2000);
        this.fetchStatus();
        this.dialogEditActions=[
            {label:'Löschen',onClick:function(){
                let url=urlbase+"?request=clearTimer&";
                url=self.addParametersToUrl(url);
                self.runCommand("Lösche Timer",url);
                self.hideDialog();
            }},
            {label:'Abbrechen',onClick:self.hideDialog},
            {label:'Ok',onClick:function(){
                let url=urlbase+"?request=updateTimer&";
                url=self.addParametersToUrl(url);
                url+="&id="+encodeURIComponent(self.state.dialogTimerId);
                self.runCommand("Update Timer",url);
                self.hideDialog();
            }}
        ];
        this.dialogNewActions=[];
        this.dialogNewActions.push(this.dialogEditActions[1]);
        this.dialogNewActions.push(
            {label:'Ok',onClick:function(){
                let url=urlbase+"?request=addTimer&";
                url+=self.addParametersToUrl(url);
                self.runCommand("Add Timer",url);
                self.hideDialog();
            }}
        );
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
        let wd=-1;
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
                <Button icon="add" floating primary onClick={this.onPlus} className="plusButton" theme={ButtonTheme}/>
                <Dialog
                    active={this.state.dialogVisible}
                    actions={this.state.dialogActions}
                    title={"Timer"}>
                    <RadioGroup value={this.state.dialogWeekday} onChange={function(v){self.vchange('dialogWeekday',v)}}>
                        {Util.weekdays.map((el)=>{
                            wd++;
                            return <RadioButton label={el} value={wd} theme={RadioTheme}/>
                        })}
                    </RadioGroup>
                    <input type="text" name="start" value={this.state.dialogStart} onChange={function(ev){self.vchange('dialogStart',ev.target.value)}}/>
                    <input type="text" name="duration" value={this.state.dialogDuration} onChange={function(ev){self.vchange('dialogDuration',ev.target.value)}}/>
                </Dialog>

            </div>
        );
    }
    vchange(name,value){
        let ns={};
        ns[name]=value;
        this.setState(ns);
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
            dialogDuration:15,
            dialogActions:this.dialogNewActions
        });
    }
}


export default TimerView;
