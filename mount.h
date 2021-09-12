#ifndef _MOUNT_H_
#define _MOUNT_H_

class MountHelper
{
    private:
        stack <string> mount_points;
    public:
        int add_mount(const char * source, const char* target, const char * file_type, unsigned long flags);
        ~MountHelper();
};

int MountHelper::add_mount(const char * source, const char* target, const char * file_type, unsigned long flags)
{
    int ret = mount(source, target, file_type, flags, NULL);
    if(ret != 0)
        errExit("Mount failed");
    mount_points.push(target);
    return ret;
}

MountHelper::~MountHelper()
{
    int flag = 0;
    while(!this->mount_points.empty())
    {
        string top = this->mount_points.top();
        this->mount_points.pop();
        if(umount(top.c_str()) != 0)
        {
            flag = 1;
            cout << "Unmounting " << top << " failed with errno " << errno << "\n";
        }
    }

}
#endif