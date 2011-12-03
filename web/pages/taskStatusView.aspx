<%@ Page Language="C#" AutoEventWireup="true" MasterPageFile="~/pages/site.master" CodeBehind="taskStatusView.aspx.cs" Inherits="Web.pages.taskStatusView" %>
<asp:Content ID="cDetail" ContentPlaceHolderID="phDetail" runat="server">
   <script type="text/javascript" src="../script/taskStatusView.js"></script>
   <div style="display: none;">
   </div>
   <div id="left_panel">
      <div class="left_tooltip">
         <img src="../images/task-status-192x192.png" alt="" />
         <div id="left_tooltip_box_outer">
            <div id="left_tooltip_box_inner">
               <p>
                  <img src="../images/tooltip.png" alt="" />The task status display shows up to the minute information on Tasks.
               </p>
               <p>
                  Rows which highlight on mouse-over will display more detailed data when clicked. 
               </p>
               <p>
                  To refresh the data select the menu choice again. 
               </p>
            </div>
         </div>
      </div>
   </div>
   <div id="content" class="display">
      <br />
      <table border="0" cellpadding="0" cellspacing="0">
         <tr>
            <td>
               <div class="ui-widget-content ui-corner-all" style="height: 165px; margin-left: 40px;">
                  <div class="ui-widget-header">
                     <span> Task Status - Active</span>
                  </div>
                  <div style="padding: 10px;">
                     <table class="jtable" cellspacing="1" cellpadding="1">
                        <thead>
                           <tr>
                              <th width="300px">Status</th>
                              <th align="center" width="100px">Total</th>
                           </tr>
                        </thead>
                        <tbody>
                           <tr tag="selectAutoTask" status="processing">
                              <td width="300px">Processing</td>
                              <td align="center" width="100px">
                                 <asp:Label ID="lblAutomatedTaskProcessing" runat="server" />
                              </td>
                           </tr>
                           <tr tag="selectAutoTask" status="staged">
                              <td width="300px">Staged</td>
                              <td align="center" width="100px">
                                 <asp:Label ID="lblAutomatedTaskStaged" runat="server" />
                              </td>
                           </tr>
                           <tr tag="selectAutoTask" status="submitted">
                              <td width="300px">Submitted</td>
                              <td align="center" width="100px">
                                 <asp:Label ID="lblAutomatedTaskSubmitted" runat="server" />
                              </td>
                           </tr>
                           <tr tag="selectAutoTask" status="pending">
                              <td width="300px">Pending</td>
                              <td align="center" width="100px">
                                 <asp:Label ID="lblAutomatedTaskPending" runat="server" />
                              </td>
                           </tr>
                           <tr tag="selectAutoTask" status="aborting">
                              <td width="300px">Aborting</td>
                              <td align="center" width="100px">
                                 <asp:Label ID="lblAutomatedTaskAborting" runat="server" />
                              </td>
                           </tr>
                           <tr tag="selectAutoTask" status="queued">
                              <td width="300px">Queued</td>
                              <td align="center" width="100px">
                                 <asp:Label ID="lblAutomatedTaskQueued" runat="server" />
                              </td>
                           </tr>
                           <tr tag="selectAutoTask" status="processing,submitted,aborting,pending,staged,queued">
                              <td width="300px">Total Active</td>
                              <td align="center" width="100px">
                                 <asp:Label ID="lblAutomatedTaskActive" runat="server" />
                              </td>
                           </tr>
                        </tbody>
                     </table>
                  </div>
               </div>
            </td>
            <td>
               <div class="ui-widget-content ui-corner-all" style="height: 165px; margin-left: 20px;">
                  <div class="ui-widget-header">
                     <span> Task Status - Completed</span>
                  </div>
                  <div style="padding: 10px;">
                     <table class="jtable" cellspacing="1" cellpadding="1">
                        <thead>
                           <tr>
                              <th width="300px">Status</th>
                              <th align="center" width="100px">Total</th>
                           </tr>
                        </thead>
                        <tbody>
                           <tr tag="selectAutoTask" status="completed">
                              <td width="300px">Completed</td>
                              <td align="center" width="100px">
                                 <asp:Label ID="lblAutomatedTaskCompleted" runat="server" />
                              </td>
                           </tr>
                           <tr tag="selectAutoTask" status="cancelled">
                              <td width="300px">Cancelled</td>
                              <td align="center" width="100px">
                                 <asp:Label ID="lblAutomatedTaskCancelled" runat="server" />
                              </td>
                           </tr>
                           <tr tag="selectAutoTask" status="error">
                              <td width="300px">Errored</td>
                              <td align="center" width="100px">
                                 <asp:Label ID="lblAutomatedTaskErrored" runat="server" />
                              </td>
                           </tr>
                           <tr tag="selectAutoTask" status="completed,cancelled,error">
                              <td width="300px">Total Completed</td>
                              <td align="center" width="100px">
                                 <asp:Label ID="lblAutomatedTaskTotalCompleted" runat="server" />
                              </td>
                           </tr>
                           <tr tag="selectAutoTask" status="">
                              <td width="300px">All Statuses</td>
                              <td align="center" width="100px">
                                 <asp:Label ID="lblAutomatedAllStatuses" runat="server" />
                              </td>
                           </tr>
                        </tbody>
                     </table>
                  </div>
               </div>
            </td>
         </tr>
      </table>
   </div>
</asp:Content>