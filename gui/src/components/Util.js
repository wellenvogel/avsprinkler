class Util{
    static startToDate(start){
        let hhmm=start.split(':');
        let d=new Date();
        d.setHours(hhmm[0]);
        d.setMinutes(hhmm[1]);
        return d;
    }
    static timerSort(x,y){
        if ( x.weekday !== y.weekday) return x.weekday - y.weekday;
        return Util.startToDate(x.start) - Util.startToDate(y.start)
    }
}
Util.weekdays=['Mo','Die','Mi','Do','Fre','Sa','So'];
export default Util;