import React, { Component } from 'react';
import {ListItem} from 'react-toolbox/lib/list'
import {Button, IconButton} from 'react-toolbox/lib/button';

class ChannelItem extends Component{
    constructor(props){
        super(props);
        this.state=props;
        this.onStart=this.onStart.bind(this);
        this.onStop=this.onStop.bind(this);
    }
    render(){
        let ltext="gesamt: "+Math.round(this.props.time/60)+" Minuten";
        let statusClass="statusOff";
        if (this.props.active){
            ltext+=", Laufzeit noch "+Math.round(this.props.remain/60)+" Minuten";
            ltext+=", Impulse="+this.props.count;
            statusClass="statusOn"
        }
        return (<ListItem
            caption={this.props.name||"Channel "+this.props.id}
            legend={ltext}
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
}
export default  ChannelItem;
