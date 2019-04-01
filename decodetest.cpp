#include <stdio.h>
#include <math.h>
#include <time.h>

#include <gsl/gsl_interp.h>
#include <gsl/gsl_spline.h>
#include <gsl/gsl_statistics.h>

#include <iostream>
using namespace std;

unsigned int getbits(unsigned int a,int left,int right)
{
    unsigned int b,c,d;
    if(left<right)
    {
        printf("'left' should be larger than 'right'\n");
        return(-1);
    }
    b=a>>(right-1);
    c=~((~0)<<(left-right+1));
    d=b&c;
    return(d);
}

int main(int argc, char *argv[])
{
    using namespace std;
    clock_t start_time=clock();

    char dirpath[]="V1730_1.bin";
    FILE* pfile;
    FILE* poutput; 
    FILE* poutput_EJ301;
    FILE* poutput_stilbene;
    FILE* poutput_x;
    pfile=fopen(dirpath,"rb");
    poutput=fopen("730_data","w");
    poutput_EJ301 = fopen("EJ301_data","w+");
    poutput_stilbene = fopen("stilbene_data","w+");
    poutput_x = fopen("x_data","w+");

    unsigned int oneline = 0;
    unsigned int ChannelMask, Ch_pre, TriggerTimeStamp;

    int recordlength = 96;   // -1 for list mode, setValue/2 for mixed mode
    int EventSize = recordlength/2 + 3;

    int BoardAggrSize = 0, ChannelAggrSize = 999999;
    int BoardlineNum = 0, ChannellineNum = 0, eventNum = 0;
    int lenBoardHeader=4, lenChannelHeader=2;
    int BAnum = 0, CAnum = 0, effectiveNum = 0;

    int EventlineNum, judge, rd;
    
    int eventPulse[recordlength];
    int timestamp, qlong, qshort;
    double peak;
    int i;

    while(!feof(pfile))
    {
        fread(&oneline,4,1,pfile);
        //auto stop, oneline will not change when stop reading

        BoardlineNum = BoardlineNum + 1;
        if (BoardlineNum == BoardAggrSize + 1)
        {
            BoardAggrSize = int(getbits(oneline,28,1));
            printf("Size of BoardAggregate is : %d\n",BoardAggrSize);
            // printf("%d %d\n", ChannellineNum, BoardlineNum);
            BoardlineNum = 1;
            BAnum = BAnum + 1;
            // printf("%d %d\n", ChannellineNum, BoardlineNum);
        }

        if (BoardlineNum == 2)
        {
            ChannelMask = getbits(oneline,8,1);
        }

        if (BoardlineNum < 5)
        {
            ChannellineNum = -1;
        }

        if (BoardlineNum == 5)
        {
            ChannellineNum = 1;
        }

        if (BoardlineNum > 5)
        {
            ChannellineNum = ChannellineNum + 1;
        }

        if (ChannellineNum%ChannelAggrSize == 1)
        {
            ChannelAggrSize = int(getbits(oneline,22,1));
            ChannellineNum = 1;
            CAnum = CAnum + 1;
        }

        if (ChannellineNum == 2)
        {
            rd = 8*int(getbits(oneline,16,1));
            if (rd != recordlength)  
            {
                printf("recordlength is %d\n", rd);
            }
        }

        if (ChannellineNum > 2)
        {
            EventlineNum = ChannellineNum-2;
            judge = EventlineNum%EventSize;
            // printf("%d %d\n", ChannellineNum, judge);
            if (judge == 1)  
            {
                timestamp = getbits(oneline,31,1);       // timestamp
                Ch_pre = getbits(oneline,32,32);
                i = 0;
                // printf("%d %d\n", timestamp, Ch_pre);
            }
            else if (judge == EventSize-1)  
            {
                //printf("EXTRA\n");
                peak = 1.0;//gsl get peak
            }
            else if (judge == 0)  
            {
                qlong = getbits(oneline,32,17);     // qlong
                qshort = getbits(oneline,15,1);      // qshort
                if (ChannelMask==1 && Ch_pre==0)
                {
                    fprintf(poutput_EJ301, "%u %d %d\n", timestamp, qlong, qshort);
                }
                else if (ChannelMask==2 && Ch_pre==0)
                {
                    fprintf(poutput_stilbene, "%u %d %d\n", timestamp, qlong, qshort);
                }
                else
                {
                    fprintf(poutput_x, "%u %d %d %d %d\n", timestamp, qlong, qshort, ChannelMask, Ch_pre);
                }
                eventNum = eventNum+1;
            }
            else
            {
                eventPulse[2*i] = int(getbits(oneline,30,17));
                eventPulse[2*i+1] = int(getbits(oneline,14,1));
                i = i+1;
            }
            
        }


        // lentmp = lineNum-lenBoardHeader;
        // if (lentmp%ChannelAggrSize == 0)
        // {
        //     ChannelAggrSize = int(getbits(oneline,22,1));
        //     //printf("Size of ChannelAggregate is : %d\n",ChannelAggrSize);
        //     CAnum = CAnum + 1;
        // }

        // if (lentmp%ChannelAggrSize>=lenChannelHeader && lentmp>=0)
        // {
        //     channellentmp = lentmp - lenChannelHeader;
        //     judge = channellentmp%(recordlength+3);
        //     if (judge == 0)
        //     {
        //         eventNum = eventNum +1;
        //         TriggerTimeStamp = getbits(oneline,31,1);
        //         Ch_pre = getbits(oneline,32,32);                    
        //         fprintf(poutput,"%-15u", TriggerTimeStamp);
        //         fprintf(poutput,"%-4u", ChannelMask + Ch_pre);          // 1 for EJ301, 2 for stilbene 
        //     }
        //     if (judge == recordlength+2)
        //     {
        //         // if (int(getbits(oneline,16,16))==1)
        //         // {
        //             // effectiveNum = effectiveNum + 1;
        //             fprintf(poutput,"%-10u", getbits(oneline,32,17));   // Qlong
        //             fprintf(poutput,"%-10u\n", getbits(oneline,15,1));    // Qshort
        //             fprintf(poutput,"%-15u", TriggerTimeStamp);
        //             fprintf(poutput,"%-4u", ChannelMask + Ch_pre);
        //             fprintf(poutput,"%-2u\n", getbits(oneline,16,16));  // pur
        //         }
        //     }
        
    }

    clock_t end_time=clock();
    cout<<endl<<"Running time is: "<<double(end_time-start_time)/CLOCKS_PER_SEC*1000<<"ms"<<endl;
    cout<<endl;
    
    printf("Size of ChannelAggregate is : %d\n",ChannelAggrSize);
    printf("Number of BoardAggregate is : %d\n",BAnum);
    printf("Number of ChannelAggregate is : %d\n",CAnum);
    printf("Number of eventNum is : %d\n",eventNum);
    // printf("Number of effectiveNum is : %d\n",effectiveNum);
    //printf("Number of lineNum is : %d\n\n",lineNum);

    // printf("channelmask is %u\n",channelmask);
    fclose(pfile);
    // fclose(poutput);
    fclose(poutput_EJ301);
    fclose(poutput_stilbene);
    fclose(poutput_x);
    return 0;
}
