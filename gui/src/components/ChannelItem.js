import React, { Component } from 'react';
import {ListItem} from 'react-toolbox/lib/list'
import {Button, IconButton} from 'react-toolbox/lib/button';
import theme from '../style/theme/listItem.less'
import baseTheme from 'react-toolbox/lib/list/theme.css';
import FontIcon from 'react-toolbox/lib/font_icon';

class ChannelItem extends Component{
    constructor(props){
        super(props);
        this.state=props;
        this.onStart=this.onStart.bind(this);
        this.onStop=this.onStop.bind(this);
        this.onItemClick=this.onItemClick.bind(this);
    }
    countToL(count){
        let ppl=this.props.ppl||1;
        return Math.round(count/ppl);
    }
    render(){
        let ltext=Math.round(this.props.time/60)+" Min/ ";
        let statusClass="statusOff";
        if (this.props.active){
            ltext+=this.countToL(this.props.count+this.props.ccount)+"l";
            ltext+=", on="+Math.round(this.props.running/60)+"/"+Math.round(this.props.runtime/60)+" Min";
            ltext+=", "+ this.countToL(this.props.ccount)+"l";
            statusClass="statusOn"
        }
        else{
            ltext+=this.countToL(this.props.count)+"l";
        }
        let caption=this.props.name||"Channel "+this.props.id;
        return (
        <div className={"channelItem " + baseTheme.listItem + " "+baseTheme.item}>
            <span className={baseTheme.itemAction}>
            {this.props.active?
                <Button label="Stop" raised className="buttonStop" onClick={this.onStop}/>
                :
                <Button label="Start" raised className="buttonStart" onClick={this.onStart}/>

            }
                </span>
            <div className="rightField" onClick={this.onItemClick}>
                <div className="info">
                    <span className={baseTheme.itemText + " " + baseTheme.primary + " "+theme.itemText}>{caption}</span>
                    <span class="info">{ltext}</span>

                </div>
                <div className="timerInfo">
                    {this.props.timerSum > 0?
                        <span><FontIcon value="timer"/>
                        <span className="timerSum">{this.props.timerNumber}/{this.props.timerSum}min</span>
                    </span>
                        :null
                    }
                </div>
            </div>

        </div>);
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
