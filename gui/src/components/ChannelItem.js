import React, { Component } from 'react';
import {ListItem} from 'react-toolbox/lib/list'
import {Button, IconButton} from 'react-toolbox/lib/button';
import theme from '../style/theme/listItem.less'

class ChannelItem extends Component{
    constructor(props){
        super(props);
        this.state=props;
        this.onStart=this.onStart.bind(this);
        this.onStop=this.onStop.bind(this);
        this.onItemClick=this.onItemClick.bind(this);
    }
    render(){
        let ltext=Math.round(this.props.time/60)+" Min/ ";
        let statusClass="statusOff";
        if (this.props.active){
            ltext+=this.props.count+this.props.ccount+" P";
            ltext+=", on="+Math.round(this.props.running/60)+"/"+Math.round(this.props.runtime/60)+" Min";
            ltext+=", "+ this.props.ccount+" P";
            statusClass="statusOn"
        }
        else{
            ltext+=this.props.count+" P";
        }
        return (<ListItem theme={theme}
            caption={this.props.name||"Channel "+this.props.id}
            legend={ltext}
            rightIcon="timer"
            onClick={this.onItemClick}
        >
            <div className={statusClass}></div>
            {this.props.active?
                <Button label="Stop" raised className="buttonStop" onClick={this.onStop}/>
                :
                <Button label="Start" raised className="buttonStart" onClick={this.onStart}/>

            }

        </ListItem>);
    }
    onStart(){
        if (this.props.onStart) this.props.onStart(this.props.id);
    }
    onStop(){
        if (this.props.onStop) this.props.onStop(this.props.id);
    }
    onItemClick(){
        if (this.props.onItemClick) this.props.onItemClick(this.props.id);
    }
}
export default  ChannelItem;
