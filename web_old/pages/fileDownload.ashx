<%@ WebHandler Language="C#" Class="Web.fileDownload" %>

using System;
using System.Web;

namespace Web
{
	public class fileDownload : System.Web.IHttpHandler
	{
		public virtual void ProcessRequest(HttpContext context)
		{
	        string sFile = context.Request.QueryString["filename"];
	        HttpResponse r = context.Response;
	        r.AddHeader("Content-Disposition", "attachment; filename=" + sFile);
	        r.ContentType = "text/plain";
	        r.WriteFile(context.Server.MapPath("~/temp/" + sFile));
		}
		public virtual bool IsReusable
		{
			get
			{
				return false;
			}
		}
	}
}