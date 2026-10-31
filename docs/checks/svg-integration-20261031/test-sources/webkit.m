#import <AppKit/AppKit.h>
#import <WebKit/WebKit.h>
NSString *scriptPath,*outputPath;
@interface Runner:NSObject<WKNavigationDelegate,WKScriptMessageHandler>
@property(strong) NSWindow *window;
@property(strong) WKWebView *web;
@property BOOL started;
@end
@implementation Runner
-(void)begin:(NSString*)url {
 WKWebViewConfiguration *config=[WKWebViewConfiguration new];
 config.websiteDataStore=[WKWebsiteDataStore nonPersistentDataStore];
 [config.userContentController addScriptMessageHandler:self name:@"resize"];
 [config.userContentController addScriptMessageHandler:self name:@"progress"];
 NSString *pre=@"window.__wkErrors=[];addEventListener('error',e=>__wkErrors.push({message:e.message,source:e.filename,line:e.lineno}));addEventListener('unhandledrejection',e=>__wkErrors.push({rejection:String(e.reason)}));";
 [config.userContentController addUserScript:[[WKUserScript alloc]initWithSource:pre injectionTime:WKUserScriptInjectionTimeAtDocumentStart forMainFrameOnly:YES]];
 self.web=[[WKWebView alloc]initWithFrame:NSMakeRect(0,0,1500,1000) configuration:config];
 self.window=[[NSWindow alloc]initWithContentRect:NSMakeRect(0,0,1500,1000) styleMask:NSWindowStyleMaskTitled backing:NSBackingStoreBuffered defer:NO];
 self.window.contentView=self.web;self.web.navigationDelegate=self;
 self.window.title=@"Namelecule — temporary WebKit check";[self.window orderFrontRegardless];
 [self.web loadRequest:[NSURLRequest requestWithURL:[NSURL URLWithString:url]]];
}
-(void)userContentController:(WKUserContentController*)u didReceiveScriptMessage:(WKScriptMessage*)message {
 if([message.name isEqualToString:@"progress"]){NSData *data=[NSJSONSerialization dataWithJSONObject:message.body options:0 error:nil];[data writeToFile:[outputPath stringByAppendingString:@".progress"] atomically:YES];return;}
 double width=[message.body doubleValue];[self.window setContentSize:NSMakeSize(width,1000)];[self.web setFrameSize:NSMakeSize(width,1000)];
}
-(void)webView:(WKWebView*)web didFinishNavigation:(WKNavigation*)navigation {
 if(self.started)return;self.started=YES;
 NSError *error=nil;NSString *script=[NSString stringWithContentsOfFile:scriptPath encoding:NSUTF8StringEncoding error:&error];
 if(!script){NSLog(@"%@",error);exit(2);}
 [web callAsyncJavaScript:script arguments:@{} inFrame:nil inContentWorld:WKContentWorld.pageWorld completionHandler:^(id result,NSError *error){
  if(error){NSLog(@"WebKit evaluation failed: %@",error);exit(1);}
  NSError *writeError=nil;BOOL ok=[(NSString*)result writeToFile:outputPath atomically:YES encoding:NSUTF8StringEncoding error:&writeError];
  if(!ok){NSLog(@"%@",writeError);exit(2);}puts("WebKit test completed");exit(0);
 }];
}
-(void)webView:(WKWebView*)web didFailProvisionalNavigation:(WKNavigation*)navigation withError:(NSError*)error {NSLog(@"WebKit navigation failed: %@",error);exit(1);}
@end
int main(int argc,const char **argv){@autoreleasepool {
 if(argc!=4)return 2;
 scriptPath=[NSString stringWithUTF8String:argv[2]];outputPath=[NSString stringWithUTF8String:argv[3]];
 NSApplication *app=NSApplication.sharedApplication;[app setActivationPolicy:NSApplicationActivationPolicyAccessory];
 Runner *runner=[Runner new];[runner begin:[NSString stringWithUTF8String:argv[1]]];
 dispatch_after(dispatch_time(DISPATCH_TIME_NOW,150*NSEC_PER_SEC),dispatch_get_main_queue(),^{puts("WebKit timed out");exit(3);});
 [app run];
}return 0;}
