#import <Foundation/Foundation.h>
#import <AVFoundation/AVFoundation.h>
#import <ImageIO/ImageIO.h>
int main(int argc,const char **argv){@autoreleasepool{
 if(argc!=4)return 2;
 AVURLAsset *asset=[AVURLAsset URLAssetWithURL:[NSURL fileURLWithPath:@(argv[1])] options:nil];
 AVAssetImageGenerator *generator=[AVAssetImageGenerator assetImageGeneratorWithAsset:asset];generator.appliesPreferredTrackTransform=YES;generator.requestedTimeToleranceBefore=kCMTimeZero;generator.requestedTimeToleranceAfter=kCMTimeZero;
 NSError *error=nil;CGImageRef image=[generator copyCGImageAtTime:CMTimeMakeWithSeconds(atof(argv[3]),600) actualTime:NULL error:&error];if(!image){NSLog(@"%@",error);return 3;}
 CGImageDestinationRef destination=CGImageDestinationCreateWithURL((__bridge CFURLRef)[NSURL fileURLWithPath:@(argv[2])],CFSTR("public.png"),1,NULL);CGImageDestinationAddImage(destination,image,NULL);BOOL ok=CGImageDestinationFinalize(destination);CFRelease(destination);CGImageRelease(image);return ok?0:4;
}}
