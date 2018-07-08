import React, { Component } from 'react';
import {ListItem} from 'react-toolbox/lib/list'
import {Button, IconButton} from 'react-toolbox/lib/button';
import theme from '../style/theme/listItem.less'

const weekdays=['Mo','Die','Mi','Do','Fre','Sa','So'];
class TimerEntry extends Component{
    constructor(props){
        super(props);
        this.state=props;
        this.onItemClick=this.onItemClick.bind(this);
    }
    weekdayToString(wd){
       if (wd < 0 || wd >= weekdays.length) return "??";
       return weekdays[wd];
    }
    render(){
        let name="";
        if (this.props.channelName !== undefined) name=": "+this.props.channelName;
        return (<ListItem theme={theme}
            caption={this.weekdayToString(this.props.weekday)+", "+this.props.start+name}
            legend={"Dauer: "+this.props.duration+" Minuten"}
            onClick={this.onItemClick}
        >
        </ListItem>);
    }
    onItemClick(){
        if (this.props.onItemClick) this.props.onItemClick(this.props);
    }
}
export default  TimerEntry;
