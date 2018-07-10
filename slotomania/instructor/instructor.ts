/*
 * This file serves as a plugin which provides a number of util functions
 * used for conmmuincating with "instructor" API. You may change this file
 * to suit your needs.
 */

import _ from "lodash";
import u from "updeep";
import { ServerState } from "./index";

export interface Operation {
  verb: "MERGE" | "ADD" | "OVERWRITE" | "DELETE";
  entity_type: "Transaction" | "Event";
  target_value: any;
}
export interface UpdateServerStateAction {
  type: "UpdateServerStateAction";
  partialStateUpdate: {
    operations: Array<Operation>;
  };
}

export const BASE_URL = `${window.location.protocol}//${
  window.location.hostname
}:${window.location.port ? "8000" : ""}/api`;

export async function callSlotoEndpoint(request: {
  endpoint: string;
  jsonBody: {};
  authToken?: string;
}) {
  const url = `${BASE_URL}/${request.endpoint}/`;
  const jwt = request.authToken
    ? request.authToken
    : sessionStorage.getItem("jwt");

  let call = await fetch(url, {
    method: "POST",
    body: JSON.stringify(request.jsonBody),
    // credentials: 'include',
    headers: {
      "Content-Type": "application/json",
      "X-Requested-With": "XMLHttpRequest",
      Authorization: jwt ? `JWT ${jwt}` : ""
    }
  });
  return call.json();
}

/*
 *  This function must exist in order to use sloto generated redux actions
 *
 */
export function callEndpoint(
  endpoint: string,
  jsonBody: {} = {},
  successCallback?: any
) {
  return async (dispatch, getState) => {
    dispatch({
      type: "callEndpoint",
      endpoint,
      ...jsonBody
    });
    const response = await callSlotoEndpoint({
      endpoint: endpoint,
      jsonBody: jsonBody,
      authToken: getState().serverState.jwt_auth_token
    });
    if (successCallback) {
      return successCallback(response);
    } else {
      dispatch({
        type: "UpdateServerStateAction",
        partialStateUpdate: response
      });
      return response;
    }
  };
}
function createReducer(initialState, handlers) {
  return function reducer(state = initialState, action) {
    if (handlers.hasOwnProperty(action.type)) {
      return handlers[action.type](state, action);
    } else {
      return state;
    }
  };
}

function applyOperation(result: ServerState, operation: Operation) {
  const targetValue = operation.target_value;
  function merge(sourceValue) {
    const oldItems = sourceValue || [];
    const dupes = oldItems.filter(item => {
      return targetValue.find(x => x.id === item.id);
    });
    return [
      ...oldItems.filter(item => {
        return !targetValue.find(x => x.id === item.id);
      }),
      ...targetValue
    ];
  }
  if (operation.verb === "OVERWRITE") {
    return u.updateIn(operation.entity_type, targetValue, result);
  } else if (operation.verb === "MERGE") {
    return u.updateIn(operation.entity_type, merge, result);
  } else if (operation.verb === "DELETE") {
    return u.updateIn(
      operation.entity_type,
      u.reject(item => {
        return item.id === targetValue.id;
      }),
      result
    );
  } else {
    throw { operation };
  }
}

const serverState = createReducer(
  {},
  {
    UpdateServerStateAction: (
      serverState: ServerState,
      action: UpdateServerStateAction
    ) => {
      let ret = Object.assign({}, serverState);
      const operations = action.partialStateUpdate.operations;
      ret = _.reduce(operations, applyOperation, ret);
      return ret;
    }
  }
);
