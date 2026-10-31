#import <Foundation/Foundation.h>
#import <AVFoundation/AVFoundation.h>
#import <CoreVideo/CoreVideo.h>
#import <ImageIO/ImageIO.h>
#import <CoreGraphics/CoreGraphics.h>
#import <unistd.h>
#import <math.h>

int main(int argc, const char **argv) { @autoreleasepool {
 if(argc!=4)return 2;
 NSError *error=nil;
 NSArray *frames=[NSJSONSerialization JSONObjectWithData:[NSData dataWithContentsOfFile:@(argv[1])] options:0 error:&error];
 double offset=[frames.firstObject[@"seconds"] doubleValue];
 NSURL *url=[NSURL fileURLWithPath:@(argv[2])];
 AVAssetWriter *writer=[[AVAssetWriter alloc] initWithURL:url fileType:AVFileTypeMPEG4 error:&error];
 NSDictionary *settings=@{AVVideoCodecKey:AVVideoCodecTypeH264,AVVideoWidthKey:@1280,AVVideoHeightKey:@800,AVVideoCompressionPropertiesKey:@{AVVideoAverageBitRateKey:@2500000,AVVideoMaxKeyFrameIntervalKey:@30}};
 AVAssetWriterInput *input=[AVAssetWriterInput assetWriterInputWithMediaType:AVMediaTypeVideo outputSettings:settings];
 NSDictionary *attributes=@{(id)kCVPixelBufferPixelFormatTypeKey:@(kCVPixelFormatType_32ARGB),(id)kCVPixelBufferWidthKey:@1280,(id)kCVPixelBufferHeightKey:@800};
 AVAssetWriterInputPixelBufferAdaptor *adaptor=[AVAssetWriterInputPixelBufferAdaptor assetWriterInputPixelBufferAdaptorWithAssetWriterInput:input sourcePixelBufferAttributes:attributes];
 [writer addInput:input];if(![writer startWriting]){NSLog(@"start: %@",writer.error);return 3;}[writer startSessionAtSourceTime:kCMTimeZero];
 for(NSDictionary *frame in frames){ @autoreleasepool {
  while(!input.readyForMoreMediaData){if(writer.status==AVAssetWriterStatusFailed){NSLog(@"write: %@",writer.error);return 4;}usleep(5000);}
  CGImageSourceRef source=CGImageSourceCreateWithURL((__bridge CFURLRef)[NSURL fileURLWithPath:frame[@"path"]],NULL);
  CGImageRef image=CGImageSourceCreateImageAtIndex(source,0,NULL);
  if(CGImageGetWidth(image)!=1280||CGImageGetHeight(image)!=800)return 5;
  CVPixelBufferRef buffer=NULL;
  NSDictionary *options=@{(id)kCVPixelBufferCGImageCompatibilityKey:@YES,(id)kCVPixelBufferCGBitmapContextCompatibilityKey:@YES};
  if(CVPixelBufferCreate(kCFAllocatorDefault,1280,800,kCVPixelFormatType_32ARGB,(__bridge CFDictionaryRef)options,&buffer)!=kCVReturnSuccess)return 6;
  CVPixelBufferLockBaseAddress(buffer,0);CGColorSpaceRef colors=CGColorSpaceCreateDeviceRGB();
  CGContextRef context=CGBitmapContextCreate(CVPixelBufferGetBaseAddress(buffer),1280,800,8,CVPixelBufferGetBytesPerRow(buffer),colors,kCGImageAlphaNoneSkipFirst);
  CGContextDrawImage(context,CGRectMake(0,0,1280,800),image);CGContextRelease(context);CGColorSpaceRelease(colors);CVPixelBufferUnlockBaseAddress(buffer,0);
  BOOL ok=[adaptor appendPixelBuffer:buffer withPresentationTime:CMTimeMakeWithSeconds([frame[@"seconds"] doubleValue]-offset,600)];CVPixelBufferRelease(buffer);CGImageRelease(image);CFRelease(source);if(!ok)return 7;
 }}
 double duration=[frames.lastObject[@"seconds"] doubleValue]-offset+0.4;
 [writer endSessionAtSourceTime:CMTimeMakeWithSeconds(duration,600)];[input markAsFinished];
 dispatch_semaphore_t done=dispatch_semaphore_create(0);[writer finishWritingWithCompletionHandler:^{dispatch_semaphore_signal(done);}];
 if(dispatch_semaphore_wait(done,dispatch_time(DISPATCH_TIME_NOW,60*NSEC_PER_SEC))||writer.status!=AVAssetWriterStatusCompleted){NSLog(@"finish: %@",writer.error);return 8;}
 AVURLAsset *asset=[AVURLAsset URLAssetWithURL:url options:nil];AVAssetTrack *track=[asset tracksWithMediaType:AVMediaTypeVideo].firstObject;
 AVAssetReader *reader=[[AVAssetReader alloc] initWithAsset:asset error:&error];
 AVAssetReaderTrackOutput *output=[[AVAssetReaderTrackOutput alloc] initWithTrack:track outputSettings:@{(id)kCVPixelBufferPixelFormatTypeKey:@(kCVPixelFormatType_32BGRA)}];[reader addOutput:output];[reader startReading];
 NSUInteger count=0;NSMutableArray *times=[NSMutableArray array];CMSampleBufferRef sample;while((sample=[output copyNextSampleBuffer])){count++;[times addObject:@(CMTimeGetSeconds(CMSampleBufferGetPresentationTimeStamp(sample)))];CFRelease(sample);}
 BOOL matched=YES;for(NSDictionary *frame in frames){double target=[frame[@"seconds"] doubleValue]-offset;BOOL found=NO;for(NSNumber *time in times)if(fabs(time.doubleValue-target)<=1.0/600+1e-8){found=YES;break;}if(!found)matched=NO;}
 NSDictionary *verification=@{@"encodedFrames":@(frames.count),@"allSourceTimestampsPresent":@(matched),@"sourceTimestampOffset":@(offset),@"decodedFrameTimestamps":times,@"decodedFrames":@(count),@"durationSeconds":@(CMTimeGetSeconds(asset.duration)),@"width":@(track.naturalSize.width),@"height":@(track.naturalSize.height),@"readCompleted":@(reader.status==AVAssetReaderStatusCompleted),@"fileBytes":@([[[NSFileManager defaultManager] attributesOfItemAtPath:@(argv[2]) error:nil] fileSize])};
 [[NSJSONSerialization dataWithJSONObject:verification options:NSJSONWritingPrettyPrinted error:nil] writeToFile:@(argv[3]) atomically:YES];
 if(!matched||count<frames.count||count>frames.count+1||reader.status!=AVAssetReaderStatusCompleted)return 9;
 printf("MP4 encoded and fully decoded: %lu frames, %.2f seconds\n",(unsigned long)count,CMTimeGetSeconds(asset.duration));
 return 0;
}}
