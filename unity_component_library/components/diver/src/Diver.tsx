import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection,
} from "streamlit-component-lib"
import "./style.css"
import React, { ReactNode } from "react"

interface State {

}

class Diver extends StreamlitComponentBase<State> {
  public state = { hovered: false }

  componentDidMount() {
    super.componentDidMount();
    Streamlit.setComponentValue(false)
    Streamlit.setFrameHeight(300)
  }

  public render = (): ReactNode => {
    const args = this.props.args;

    return (
      <div className="diver" onClick={this.onClicked}>
          <img src={"https://picsum.photos/300"} height={200} />
          <p>{args.marker}</p>
      </div>
    )
  }

  private onClicked = (): void => {
    Streamlit.setComponentValue(true)
  }

}

export default withStreamlitConnection(Diver)