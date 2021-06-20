import React, { Component } from 'react';
import Dialog from 'react-toolbox/lib/dialog';
import {RadioGroup,RadioButton} from 'react-toolbox/lib/radio';
import Util from './Util';
import RadioTheme from '../style/theme/radioButton.less';
import Input from 'react-toolbox/lib/input';
const urlbase="/control";
class TimerEdit extends Component {

    constructor(props){
        super(props);
        this.state=props;
        this.vchange=this.vchange.bind(this);
        this.timeChange=this.timeChange.bind(this);
        this.hideDialog=this.hideDialog.bind(this);
        let self=this;
        this.dialogDisabledActions=[
            {label:'Löschen',onClick:function(){
                    let url=urlbase+"?request=clearTimer&";
                    url=self.addParametersToUrl(url);
                    self.runCommand("Lösche Timer",url);
                    self.hideDialog();
                }},
            {label:'Abbrechen',onClick:self.hideDialog}
        ];
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
                self.state.callback(self.state)
            }
        })
    }
    addParametersToUrl(url){
        url+="channel="+encodeURIComponent(this.state.dialogChannel);
        url+="&start="+encodeURIComponent(this.state.dialogStart);
        url+="&weekday="+encodeURIComponent(this.state.dialogWeekday);
        url+="&duration="+encodeURIComponent(this.state.dialogDuration);
        return url;
    }
    componentDidMount(){
    }
    componentWillUnmount(){
    }
    componentWillReceiveProps(nprops){
        //this.setState(nprops);
    }
    render() {
        if (! this.state.dialogVisible) return null;
        let self=this;
        let wd=-1;
        let dialogActions=this.state.dialogTimerId?
            (this.state.timerEnabled?this.dialogEditActions:this.dialogDisabledActions)
            :this.dialogNewActions;
        return(
                <Dialog
                    active={this.state.dialogVisible}
                    actions={dialogActions}
                    title={this.state.dialogTitle?this.state.dialogTitle:"Timer"}>
                    <RadioGroup value={this.state.dialogWeekday} onChange={function(v){self.vchange('dialogWeekday',v)}}>
                        {Util.weekdays.map((el)=>{
                            wd++;
                            return <RadioButton label={el} value={wd} theme={RadioTheme}/>
                        })}
                    </RadioGroup>
                    <Input type="text" label="Start" value={this.state.dialogStart} onChange={self.timeChange}/>
                    <Input type="text" name="duration" label="Dauer(Min)" value={this.state.dialogDuration} onChange={function(value){self.vchange('dialogDuration',value)}}/>
                </Dialog>
        );
    }

    vchange(name,value){
        if (! this.state.timerEnabled) return;
        let ns={};
        ns[name]=value;
        this.setState(ns);
    }
    timeChange(value){
        if (! this.state.timerEnabled) return;
        this.setState({
            dialogStart:value
        });
    }
    hideDialog(){
        this.setState({dialogVisible:false});
        if (this.state.hideCallback){
            this.state.hideCallback();
        }
    }
    goBack(){
        this.props.history.goBack();
    }
    startToDate(start){
        let hhmm=start.split(':');
        let d=new Date();
        d.setHours(hhmm[0]);
        d.setMinutes(hhmm[1]);
        return d;
    }
}


export default TimerEdit;
