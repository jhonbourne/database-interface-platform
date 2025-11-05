
function InfoBoard(props) {
    return (
        <div>
            <p>The parameter in body is: {props.resultBodyValue}</p>
            <p>The parameter in param is: {props.resultParamValue}</p>
        </div>        
    );
}

export default InfoBoard