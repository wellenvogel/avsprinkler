import React, { Component } from 'react';
import ToolBar from './components/ToolBar';
import {List,ListItem} from 'react-toolbox/lib/list';


const urlbase="/control";
class HistoryView extends Component {

    constructor(props){
        super(props);
        this.state=props;
        this.goBack=this.goBack.bind(this);
        this.fetchStatus=this.fetchStatus.bind(this);
        this.onItemClick=this.onItemClick.bind(this);
    }
    fetchStatus(){
        let self=this;
        fetch(urlbase+"?request=history",{
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
        let self=this;
        this.fetchStatus();
    }
    componentWillUnmount(){
    }
    getEntries(){
        if (! this.state.data) return [];
        let rt=[];
        this.state.data.forEach(function(e){
            let param=e.split(',');
            let dtkind=param[0].split('-');
            if (dtkind[1] !== "STOP") return;
            let re={};
            re.datev=new Date(dtkind[0]);
            re.date=dtkind[0];
            re.info=param[2]+": "+Math.round(param[5]/60)+"min, "+param[6]+"l (Sum: "+Math.round(param[3]/60)+"min/ "+param[4]+"l)";
            rt.push(re);
        });
        rt.sort(function(x,y){
            return y.datev - x.datev;
        });
        return rt;
    }
    render() {
        let self=this;
        let info=this.state;
        let title="Historie";
        let entries=this.getEntries();
        return (
            <div className="view historyView">
                <ToolBar leftIcon="arrow_back"
                         leftClick={this.goBack}>
                    <span className="toolbar-label">{title}</span>
                    <span className="spacer"/>
                </ToolBar>
                <div className="mainDiv">
                    <List>
                        {entries ?
                            entries.map(function (te) {
                                return <ListItem caption={te.date} legend={te.info}/>
                            })
                            :
                            <p>Loading...</p>
                        }
                    </List>
                </div>
            </div>
        );
    }
    goBack(){
        this.props.history.goBack();
    }
    onItemClick(te){
    }

}


export default HistoryView;
