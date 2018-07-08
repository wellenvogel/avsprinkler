import React, { Component } from 'react';
import {
    HashRouter as Router,
    Route
} from 'react-router-dom';

import MainView from './MainView';
import TimerView from './TimerView';
class App extends Component {
  render() {
    return (
        <Router>
            <div className="main">
                <Route exact path="/" component={MainView}/>
                <Route path="/overview" component={MainView}/>
                <Route path="/timer/:channel" component={TimerView}/>
            </div>
        </Router>
    );
  }
}

export default App;
