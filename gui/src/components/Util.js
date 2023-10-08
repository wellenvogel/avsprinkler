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
    static dateToStart(date){
        let h=date.getHours();
        h=((h<10)?"0":"")+h;
        let m=date.getMinutes();
        m=((m<10)?"0":"")+m;
        return h+":"+m;
    }
    static addDuration(start,duration){
        let d=Util.startToDate(start);
        d.setTime(d.getTime()+duration*60*1000);
        return Util.dateToStart(d);
    }
}
Util.weekdays=['Mo','Die','Mi','Do','Fre','Sa','So'];
export default Util;